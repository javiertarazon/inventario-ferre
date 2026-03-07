"""
Detect and optionally deduplicate repeated products by descripcion + stock + categoria.

Default mode is report-only (no database changes).
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure project root is importable when running this script directly.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db
from app.models import ItemGroup, Product
from app.utils.code_generator import CodeGenerator


@dataclass
class ProductRow:
    id: int
    codigo: str
    descripcion: str
    stock: int
    categoria_id: int | None
    categoria_nombre: str
    created_at: datetime | None


@dataclass
class DuplicateGroup:
    key: Tuple[str, int, str]
    keep: ProductRow
    duplicates: List[ProductRow]


def normalize_description(text: str) -> str:
    return " ".join((text or "").strip().split())


def load_active_products() -> List[ProductRow]:
    rows = (
        db.session.query(Product, ItemGroup.name)
        .outerjoin(ItemGroup, Product.item_group_id == ItemGroup.id)
        .filter(Product.deleted_at.is_(None))
        .all()
    )

    products: List[ProductRow] = []
    for product, category_name in rows:
        products.append(
            ProductRow(
                id=product.id,
                codigo=product.codigo,
                descripcion=product.descripcion,
                stock=int(product.stock or 0),
                categoria_id=product.item_group_id,
                categoria_nombre=category_name or "SIN_CATEGORIA",
                created_at=product.created_at,
            )
        )
    return products


def detect_duplicate_groups(products: List[ProductRow]) -> List[DuplicateGroup]:
    groups: Dict[Tuple[str, int, str], List[ProductRow]] = {}

    for p in products:
        key = (normalize_description(p.descripcion).upper(), p.stock, p.categoria_nombre.upper())
        groups.setdefault(key, []).append(p)

    duplicate_groups: List[DuplicateGroup] = []
    for key, items in groups.items():
        if len(items) < 2:
            continue

        # Keep oldest record to preserve continuity.
        ordered = sorted(items, key=lambda x: ((x.created_at or datetime.max), x.id))
        keep = ordered[0]
        duplicates = ordered[1:]

        duplicate_groups.append(DuplicateGroup(key=key, keep=keep, duplicates=duplicates))

    duplicate_groups.sort(key=lambda g: (g.key[2], g.key[0], g.key[1]))
    return duplicate_groups


def export_report_csv(groups: List[DuplicateGroup], file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "grupo",
                "accion",
                "id",
                "codigo",
                "descripcion",
                "stock",
                "categoria",
                "created_at",
            ]
        )

        for idx, group in enumerate(groups, start=1):
            all_items = [group.keep] + group.duplicates
            for item in all_items:
                action = "KEEP" if item.id == group.keep.id else "DELETE"
                writer.writerow(
                    [
                        idx,
                        action,
                        item.id,
                        item.codigo,
                        item.descripcion,
                        item.stock,
                        item.categoria_nombre,
                        item.created_at.isoformat() if item.created_at else "",
                    ]
                )


def print_report(groups: List[DuplicateGroup], max_groups: int) -> None:
    total_groups = len(groups)
    total_duplicate_rows = sum(len(g.duplicates) for g in groups)

    print("=" * 88)
    print("REPORTE DE DUPLICADOS (descripcion + stock + categoria)")
    print("=" * 88)
    print(f"Grupos duplicados: {total_groups}")
    print(f"Registros sugeridos para eliminar: {total_duplicate_rows}")

    if total_groups == 0:
        print("\nNo se detectaron duplicados con el criterio solicitado.")
        return

    print("\nDetalle:")
    to_show = groups[:max_groups]
    for idx, group in enumerate(to_show, start=1):
        desc, stock, cat = group.key
        print("-" * 88)
        print(f"Grupo {idx}: categoria={cat}, stock={stock}, descripcion={desc}")
        print(
            f"  KEEP   -> id={group.keep.id}, codigo={group.keep.codigo}, "
            f"created_at={group.keep.created_at}"
        )
        for d in group.duplicates:
            print(f"  DELETE -> id={d.id}, codigo={d.codigo}, created_at={d.created_at}")

    if total_groups > max_groups:
        print("-" * 88)
        print(f"Mostrando {max_groups} de {total_groups} grupos. Usa --max-groups para ver mas.")


def soft_delete_duplicates(groups: List[DuplicateGroup]) -> Tuple[int, List[int]]:
    deleted_count = 0
    deleted_ids: List[int] = []

    ids_to_delete = [d.id for g in groups for d in g.duplicates]
    if not ids_to_delete:
        return 0, []

    now = datetime.utcnow()
    products = Product.query.filter(Product.id.in_(ids_to_delete), Product.deleted_at.is_(None)).all()
    for p in products:
        p.deleted_at = now
        # Free unique codigo so future recoding can reuse business codes safely.
        p.codigo = f"DEL-{p.id:06d}-{now.strftime('%Y%m%d%H%M%S')}"
        deleted_count += 1
        deleted_ids.append(p.id)

    db.session.flush()
    return deleted_count, deleted_ids


def reorganize_codes_for_active_products() -> Tuple[int, List[str]]:
    """Regenerate codes for active products under current business rule."""
    updated = 0
    warnings: List[str] = []

    products = (
        Product.query.filter_by(deleted_at=None)
        .order_by(Product.item_group_id.asc(), Product.descripcion.asc(), Product.id.asc())
        .all()
    )

    # Build deterministic final codes in-memory, grouped by category prefix + initials.
    groups: Dict[Tuple[str, str], List[Product]] = {}
    for product in products:
        category_name = product.item_group.name if product.item_group else "Unknown"
        category_prefix = CodeGenerator.CATEGORY_PREFIXES.get(category_name, 'X')
        initials = CodeGenerator.get_description_initials(product.descripcion)
        key = (category_prefix, initials)
        groups.setdefault(key, []).append(product)

    final_codes_by_id: Dict[int, str] = {}
    for (prefix, initials), items in groups.items():
        ordered_items = sorted(items, key=lambda p: (p.descripcion.upper(), p.id))
        if len(ordered_items) > 99:
            warnings.append(
                f"Grupo {prefix}-{initials} excede 99 items activos ({len(ordered_items)}); "
                "solo se recodificaran los primeros 99."
            )

        for idx, product in enumerate(ordered_items, start=1):
            if idx > 99:
                continue
            final_codes_by_id[product.id] = f"{prefix}-{initials}-{idx:02d}"

    # Free final codes that may still be occupied by soft-deleted records.
    desired_codes = set(final_codes_by_id.values())
    if desired_codes:
        conflicts = Product.query.filter(
            Product.codigo.in_(desired_codes),
            Product.id.notin_(list(final_codes_by_id.keys())),
        ).all()
        now = datetime.utcnow()
        for conflict in conflicts:
            if conflict.deleted_at is None:
                warnings.append(
                    f"Conflicto activo no esperado: id={conflict.id}, codigo={conflict.codigo}."
                )
                continue
            conflict.codigo = f"DEL-{conflict.id:06d}-{now.strftime('%Y%m%d%H%M%S')}"

    # Phase 1: assign temporary unique codes to avoid UNIQUE collisions while swapping.
    for product in products:
        if product.id not in final_codes_by_id:
            continue
        product.codigo = f"TMP-{product.id:06d}"

    db.session.flush()

    # Phase 2: assign final deterministic codes.
    for product in products:
        final_code = final_codes_by_id.get(product.id)
        if not final_code:
            continue
        if product.codigo != final_code:
            product.codigo = final_code
            updated += 1

    db.session.flush()
    return updated, warnings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detecta duplicados por descripcion + stock + categoria y opcionalmente los elimina."
    )
    parser.add_argument(
        "--mode",
        choices=["report", "apply"],
        default="report",
        help="report: solo mostrar. apply: eliminar duplicados y reorganizar codigos.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirmacion explicita requerida para modo apply.",
    )
    parser.add_argument(
        "--max-groups",
        type=int,
        default=80,
        help="Cantidad maxima de grupos a mostrar en consola.",
    )
    parser.add_argument(
        "--export-csv",
        type=str,
        default="",
        help="Ruta opcional para exportar el reporte CSV.",
    )

    args = parser.parse_args()

    app = create_app("development")
    with app.app_context():
        products = load_active_products()
        groups = detect_duplicate_groups(products)

        print_report(groups, args.max_groups)

        if args.export_csv:
            out_path = Path(args.export_csv)
            export_report_csv(groups, out_path)
            print(f"\nReporte CSV exportado en: {out_path}")

        if args.mode == "report":
            print("\nModo reporte finalizado. No se realizaron cambios.")
            return

        if not args.yes:
            print("\nModo apply requiere --yes para evitar borrados accidentales.")
            return

        deleted_count, deleted_ids = soft_delete_duplicates(groups)
        updated_codes, warnings = reorganize_codes_for_active_products()
        db.session.commit()

        print("\n" + "=" * 88)
        print("APLICACION COMPLETADA")
        print("=" * 88)
        print(f"Registros eliminados (soft delete): {deleted_count}")
        print(f"Codigos reorganizados: {updated_codes}")

        if deleted_ids:
            print(f"IDs eliminados: {', '.join(str(i) for i in deleted_ids[:120])}")
            if len(deleted_ids) > 120:
                print(f"... y {len(deleted_ids) - 120} IDs mas")

        if warnings:
            print("\nAdvertencias de reorganizacion:")
            for w in warnings[:30]:
                print(f"- {w}")
            if len(warnings) > 30:
                print(f"... y {len(warnings) - 30} advertencias mas")


if __name__ == "__main__":
    main()
