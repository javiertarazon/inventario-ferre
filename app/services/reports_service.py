"""
Reports Service - Business logic for generating inventory and sales reports.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from flask import current_app
from sqlalchemy import func, and_

from app.models import Product, Movimiento, SalesOrder, SalesOrderItem, Proveedor, ItemGroup, ExchangeRate
from app.extensions import db


class ReportsService:
    """Service for generating business reports."""

    # -------------------------------------------------------------------------
    # Inventario completo
    # -------------------------------------------------------------------------

    def get_inventario_completo(self) -> List[Dict[str, Any]]:
        """
        Return full inventory list with current prices.

        Returns:
            List of dicts with product data including valor total en USD.
        """
        try:
            exchange = self._get_current_rate()
            products = (
                Product.query
                .filter_by(deleted_at=None)
                .order_by(Product.codigo)
                .all()
            )
            rows = []
            for p in products:
                precio_usd = float(p.precio_dolares or 0)
                factor = float(p.factor_ajuste or 1)
                precio_ajustado_usd = round(precio_usd * factor, 2)
                precio_bs = round(precio_ajustado_usd * exchange, 2)
                rows.append({
                    'id': p.id,
                    'codigo': p.codigo,
                    'descripcion': p.descripcion,
                    'stock': p.stock,
                    'precio_dolares': precio_usd,
                    'factor_ajuste': factor,
                    'precio_ajustado_usd': precio_ajustado_usd,
                    'precio_bs': precio_bs,
                    'valor_total_usd': round(p.stock * precio_ajustado_usd, 2),
                    'valor_total_bs': round(p.stock * precio_bs, 2),
                    'proveedor': p.proveedor.nombre if p.proveedor else '',
                    'categoria': p.item_group.name if p.item_group else '',
                    'stock_status': p.get_stock_status() if hasattr(p, 'get_stock_status') else 'ok',
                })
            return rows
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_inventario_completo error: {e}")
            return []

    # -------------------------------------------------------------------------
    # Stock bajo
    # -------------------------------------------------------------------------

    def get_stock_bajo(self) -> List[Dict[str, Any]]:
        """
        Return products at or below reorder point.

        Returns:
            List of dicts with low-stock products.
        """
        try:
            products = (
                Product.query
                .filter(
                    Product.deleted_at == None,
                    Product.stock <= Product.reorder_point
                )
                .order_by(Product.stock.asc())
                .all()
            )
            rows = []
            for p in products:
                rows.append({
                    'id': p.id,
                    'codigo': p.codigo,
                    'descripcion': p.descripcion,
                    'stock': p.stock,
                    'reorder_point': p.reorder_point,
                    'reorder_quantity': p.reorder_quantity,
                    'deficit': max(0, p.reorder_point - p.stock),
                    'proveedor': p.proveedor.nombre if p.proveedor else '',
                    'categoria': p.item_group.name if p.item_group else '',
                    'agotado': p.stock == 0,
                })
            return rows
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_stock_bajo error: {e}")
            return []

    # -------------------------------------------------------------------------
    # Movimientos por periodo
    # -------------------------------------------------------------------------

    def get_movimientos_periodo(
        self,
        start_date: date,
        end_date: date,
        tipo: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return movements in a date range.

        Args:
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            tipo: Optional filter 'ENTRADA' or 'SALIDA'.

        Returns:
            List of movement dicts.
        """
        try:
            query = Movimiento.query.filter(
                Movimiento.deleted_at == None,
                Movimiento.fecha >= start_date,
                Movimiento.fecha <= end_date,
            )
            if tipo:
                query = query.filter(Movimiento.tipo == tipo.upper())
            movimientos = query.order_by(Movimiento.fecha.desc()).all()

            rows = []
            for m in movimientos:
                rows.append({
                    'id': m.id,
                    'fecha': m.fecha,
                    'tipo': m.tipo,
                    'cantidad': m.cantidad,
                    'producto_codigo': m.producto.codigo if m.producto else '',
                    'producto_descripcion': m.producto.descripcion if m.producto else '',
                    'descripcion': m.descripcion or '',
                    'usuario': m.creator.username if m.creator else 'Sistema',
                })
            return rows
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_movimientos_periodo error: {e}")
            return []

    def get_resumen_movimientos(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Return summary totals for movement report."""
        try:
            all_m = self.get_movimientos_periodo(start_date, end_date)
            entradas = [m for m in all_m if m['tipo'] == 'ENTRADA']
            salidas = [m for m in all_m if m['tipo'] == 'SALIDA']
            return {
                'total': len(all_m),
                'total_entradas': len(entradas),
                'total_salidas': len(salidas),
                'unidades_entradas': sum(m['cantidad'] for m in entradas),
                'unidades_salidas': sum(m['cantidad'] for m in salidas),
            }
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_resumen_movimientos error: {e}")
            return {'total': 0, 'total_entradas': 0, 'total_salidas': 0,
                    'unidades_entradas': 0, 'unidades_salidas': 0}

    # -------------------------------------------------------------------------
    # Ventas por periodo
    # -------------------------------------------------------------------------

    def get_ventas_periodo(
        self,
        start_date: date,
        end_date: date,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return sales orders in a date range.

        Args:
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            status: Optional order status filter.

        Returns:
            List of sales order dicts.
        """
        try:
            query = SalesOrder.query.filter(
                SalesOrder.deleted_at == None,
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date,
            )
            if status:
                query = query.filter(SalesOrder.status == status)
            orders = query.order_by(SalesOrder.order_date.desc()).all()

            rows = []
            for o in orders:
                rows.append({
                    'id': o.id,
                    'order_number': o.order_number,
                    'order_date': o.order_date,
                    'status': o.status,
                    'payment_status': o.payment_status,
                    'customer': o.customer.name if o.customer else '',
                    'total_amount': float(o.total_amount or 0),
                    'paid_amount': float(o.paid_amount or 0),
                    'pending_amount': float((o.total_amount or 0) - (o.paid_amount or 0)),
                    'items_count': o.items.count(),
                })
            return rows
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_ventas_periodo error: {e}")
            return []

    def get_resumen_ventas(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Return summary totals for sales report."""
        try:
            orders = self.get_ventas_periodo(start_date, end_date)
            total_ventas = sum(o['total_amount'] for o in orders)
            total_cobrado = sum(o['paid_amount'] for o in orders)
            total_pendiente = sum(o['pending_amount'] for o in orders)
            por_status: Dict[str, int] = {}
            for o in orders:
                por_status[o['status']] = por_status.get(o['status'], 0) + 1
            return {
                'total_ordenes': len(orders),
                'total_ventas': round(total_ventas, 2),
                'total_cobrado': round(total_cobrado, 2),
                'total_pendiente': round(total_pendiente, 2),
                'por_status': por_status,
            }
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_resumen_ventas error: {e}")
            return {'total_ordenes': 0, 'total_ventas': 0,
                    'total_cobrado': 0, 'total_pendiente': 0, 'por_status': {}}

    # -------------------------------------------------------------------------
    # Productos mas vendidos
    # -------------------------------------------------------------------------

    def get_top_productos(
        self,
        limit: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return top selling products by quantity.

        Args:
            limit: Max number of products to return.
            start_date: Optional start date filter.
            end_date: Optional end date filter.

        Returns:
            List of product dicts with sales totals.
        """
        try:
            query = (
                db.session.query(
                    Product.id,
                    Product.codigo,
                    Product.descripcion,
                    Product.stock,
                    func.sum(SalesOrderItem.quantity).label('total_qty'),
                    func.sum(SalesOrderItem.total_price).label('total_sales'),
                )
                .join(SalesOrderItem, Product.id == SalesOrderItem.product_id)
                .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
                .filter(
                    Product.deleted_at == None,
                    SalesOrder.deleted_at == None,
                )
            )
            if start_date:
                query = query.filter(SalesOrder.order_date >= start_date)
            if end_date:
                query = query.filter(SalesOrder.order_date <= end_date)

            results = (
                query
                .group_by(Product.id, Product.codigo, Product.descripcion, Product.stock)
                .order_by(func.sum(SalesOrderItem.quantity).desc())
                .limit(limit)
                .all()
            )

            rows = []
            for idx, r in enumerate(results, start=1):
                rows.append({
                    'rank': idx,
                    'id': r.id,
                    'codigo': r.codigo,
                    'descripcion': r.descripcion,
                    'stock': r.stock,
                    'total_qty': int(r.total_qty or 0),
                    'total_sales': round(float(r.total_sales or 0), 2),
                })
            return rows
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_top_productos error: {e}")
            return []

    # -------------------------------------------------------------------------
    # Libro de Inventario (Art. 177 ISLR Venezuela)
    # -------------------------------------------------------------------------

    def get_libro_inventario(self, fecha: date) -> Dict[str, Any]:
        """
        Generate Libro de Inventario diario for a given date (Art. 177 ISLR).

        Args:
            fecha: Date to generate the report for.

        Returns:
            Dict with header info and line items.
        """
        try:
            exchange_rate = self._get_current_rate()
            products = (
                Product.query
                .filter_by(deleted_at=None)
                .order_by(Product.codigo)
                .all()
            )

            items = []
            total_usd = 0.0
            total_bs = 0.0

            for p in products:
                precio_usd = float(p.precio_dolares or 0)
                factor = float(p.factor_ajuste or 1)
                precio_ajustado = round(precio_usd * factor, 2)
                precio_bs = round(precio_ajustado * exchange_rate, 2)
                valor_usd = round(p.stock * precio_ajustado, 2)
                valor_bs = round(p.stock * precio_bs, 2)

                total_usd += valor_usd
                total_bs += valor_bs

                items.append({
                    'codigo': p.codigo,
                    'descripcion': p.descripcion,
                    'stock': p.stock,
                    'precio_usd': precio_ajustado,
                    'precio_bs': precio_bs,
                    'valor_usd': valor_usd,
                    'valor_bs': valor_bs,
                    'proveedor': p.proveedor.nombre if p.proveedor else '',
                })

            return {
                'fecha': fecha,
                'exchange_rate': exchange_rate,
                'items': items,
                'total_productos': len(items),
                'total_usd': round(total_usd, 2),
                'total_bs': round(total_bs, 2),
                'empresa': 'INVERSIONES FERRE-EXITO, C.A',
                'rif': 'J-000000000',
            }
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_libro_inventario error: {e}")
            return {
                'fecha': fecha,
                'exchange_rate': 0,
                'items': [],
                'total_productos': 0,
                'total_usd': 0,
                'total_bs': 0,
                'empresa': 'INVERSIONES FERRE-EXITO, C.A',
                'rif': 'J-000000000',
            }

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_current_rate(self) -> float:
        """Return the most recent USD exchange rate, defaulting to 1.0."""
        try:
            rate = ExchangeRate.get_current_rate()
            if rate:
                return float(rate.rate)
            return 1.0
        except Exception:
            return 1.0

    def get_default_date_range(self, days: int = 30) -> tuple[date, date]:
        """Return (start_date, end_date) tuple for the last N days."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date

    # -------------------------------------------------------------------------
    # Libro Diario de Movimientos
    # -------------------------------------------------------------------------

    def get_libro_diario(
        self,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        Return movements in journal (libro diario) format for a date range.

        For each product that had movements in the period, shows:
          - stock_apertura  : stock at the START of the period
          - movements list  : each movement chronologically
          - stock_cierre    : stock at the END of the period

        Stock apertura is reconstructed backwards from current stock.

        Args:
            start_date: Start date (inclusive).
            end_date:   End date (inclusive).

        Returns:
            Dict with 'asientos' (journal entries) and summary totals.
        """
        try:
            exchange_rate = self._get_current_rate()

            # All movements in the period, ordered by date then product
            movimientos = (
                Movimiento.query
                .filter(
                    Movimiento.deleted_at == None,
                    func.date(Movimiento.fecha) >= start_date,
                    func.date(Movimiento.fecha) <= end_date,
                )
                .order_by(Movimiento.fecha.asc(), Movimiento.id.asc())
                .all()
            )

            # Movements AFTER the period (to reconstruct opening stock)
            movimientos_despues = (
                db.session.query(
                    Movimiento.producto_id,
                    Movimiento.tipo,
                    func.sum(Movimiento.cantidad).label('total'),
                )
                .filter(
                    Movimiento.deleted_at == None,
                    func.date(Movimiento.fecha) > end_date,
                )
                .group_by(Movimiento.producto_id, Movimiento.tipo)
                .all()
            )

            # Build post-period delta per product: {product_id: net_after}
            delta_despues: Dict[int, int] = {}
            for m in movimientos_despues:
                pid = m.producto_id
                delta_despues.setdefault(pid, 0)
                if m.tipo.upper() == 'ENTRADA':
                    delta_despues[pid] += m.total
                else:
                    delta_despues[pid] -= m.total

            # Movements IN the period per product
            delta_periodo: Dict[int, int] = {}
            for m in movimientos:
                pid = m.producto_id
                delta_periodo.setdefault(pid, 0)
                if m.tipo.upper() == 'ENTRADA':
                    delta_periodo[pid] += m.cantidad
                else:
                    delta_periodo[pid] -= m.cantidad

            # Fetch all products that moved
            product_ids = list({m.producto_id for m in movimientos})
            products = {
                p.id: p for p in Product.query.filter(Product.id.in_(product_ids)).all()
            } if product_ids else {}

            # Build journal entries grouped by date
            from collections import defaultdict
            by_date: Dict[date, list] = defaultdict(list)
            for m in movimientos:
                fecha_mov = m.fecha.date() if isinstance(m.fecha, datetime) else m.fecha
                by_date[fecha_mov].append(m)

            # Calculate stock at END of period for each product:
            # stock_cierre = current_stock - delta_after_period
            # stock_apertura = stock_cierre - delta_periodo
            asientos = []
            for d in sorted(by_date.keys()):
                day_movs = by_date[d]
                lineas = []
                for m in day_movs:
                    p = products.get(m.producto_id)
                    if not p:
                        continue
                    precio_usd = float(p.precio_dolares or 0) * float(p.factor_ajuste or 1)
                    lineas.append({
                        'id': m.id,
                        'hora': m.created_at.strftime('%H:%M') if m.created_at else '--:--',
                        'tipo': m.tipo.upper(),
                        'cantidad': m.cantidad,
                        'producto_id': p.id,
                        'codigo': p.codigo,
                        'descripcion': p.descripcion,
                        'descripcion_mov': m.descripcion or '',
                        'usuario': m.creator.username if m.creator else 'Sistema',
                        'precio_usd': round(precio_usd, 2),
                        'valor_usd': round(m.cantidad * precio_usd, 2),
                        'valor_bs': round(m.cantidad * precio_usd * exchange_rate, 2),
                    })
                asientos.append({'fecha': d, 'lineas': lineas})

            # Summary per product for sidebar/totals
            resumen_productos = []
            for pid in product_ids:
                p = products.get(pid)
                if not p:
                    continue
                delta_after = delta_despues.get(pid, 0)
                stock_cierre = p.stock - delta_after
                stock_apertura = stock_cierre - delta_periodo.get(pid, 0)
                precio_usd = float(p.precio_dolares or 0) * float(p.factor_ajuste or 1)
                resumen_productos.append({
                    'codigo': p.codigo,
                    'descripcion': p.descripcion,
                    'stock_apertura': max(0, stock_apertura),
                    'entradas': sum(
                        m.cantidad for m in movimientos
                        if m.producto_id == pid and m.tipo.upper() == 'ENTRADA'
                    ),
                    'salidas': sum(
                        m.cantidad for m in movimientos
                        if m.producto_id == pid and m.tipo.upper() == 'SALIDA'
                    ),
                    'stock_cierre': max(0, stock_cierre),
                    'precio_usd': round(precio_usd, 2),
                    'valor_cierre_usd': round(max(0, stock_cierre) * precio_usd, 2),
                    'valor_cierre_bs': round(max(0, stock_cierre) * precio_usd * exchange_rate, 2),
                })
            resumen_productos.sort(key=lambda x: x['codigo'])

            total_entradas = sum(r['entradas'] for r in resumen_productos)
            total_salidas = sum(r['salidas'] for r in resumen_productos)

            return {
                'start_date': start_date,
                'end_date': end_date,
                'exchange_rate': exchange_rate,
                'asientos': asientos,
                'resumen_productos': resumen_productos,
                'total_movimientos': len(movimientos),
                'total_entradas': total_entradas,
                'total_salidas': total_salidas,
                'empresa': 'INVERSIONES FERRE-EXITO, C.A',
            }
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_libro_diario error: {e}")
            return {
                'start_date': start_date,
                'end_date': end_date,
                'exchange_rate': 1.0,
                'asientos': [],
                'resumen_productos': [],
                'total_movimientos': 0,
                'total_entradas': 0,
                'total_salidas': 0,
                'empresa': 'INVERSIONES FERRE-EXITO, C.A',
            }

    # -------------------------------------------------------------------------
    # Resumen Mensual
    # -------------------------------------------------------------------------

    def get_resumen_mensual(self, year: int, month: int) -> Dict[str, Any]:
        """
        Return monthly inventory summary.

        Opening balance = closing balance of the previous month,
        reconstructed backwards from current stock.

        Args:
            year:  Year (e.g. 2026).
            month: Month 1-12.

        Returns:
            Dict with per-product rows and totals.
        """
        try:
            from calendar import monthrange
            exchange_rate = self._get_current_rate()

            # Date boundaries for the requested month
            first_day = date(year, month, 1)
            last_day = date(year, month, monthrange(year, month)[1])

            # Movements AFTER the month (to compute stock at month-close backwards)
            delta_after: Dict[int, int] = {}
            rows_after = (
                db.session.query(
                    Movimiento.producto_id,
                    Movimiento.tipo,
                    func.sum(Movimiento.cantidad).label('total'),
                )
                .filter(
                    Movimiento.deleted_at == None,
                    func.date(Movimiento.fecha) > last_day,
                )
                .group_by(Movimiento.producto_id, Movimiento.tipo)
                .all()
            )
            for r in rows_after:
                delta_after.setdefault(r.producto_id, 0)
                if r.tipo.upper() == 'ENTRADA':
                    delta_after[r.producto_id] += r.total
                else:
                    delta_after[r.producto_id] -= r.total

            # Movements IN the month (entries and exits per product)
            entradas_mes: Dict[int, int] = {}
            salidas_mes:  Dict[int, int] = {}
            rows_mes = (
                db.session.query(
                    Movimiento.producto_id,
                    Movimiento.tipo,
                    func.sum(Movimiento.cantidad).label('total'),
                )
                .filter(
                    Movimiento.deleted_at == None,
                    func.date(Movimiento.fecha) >= first_day,
                    func.date(Movimiento.fecha) <= last_day,
                )
                .group_by(Movimiento.producto_id, Movimiento.tipo)
                .all()
            )
            for r in rows_mes:
                if r.tipo.upper() == 'ENTRADA':
                    entradas_mes[r.producto_id] = entradas_mes.get(r.producto_id, 0) + r.total
                else:
                    salidas_mes[r.producto_id] = salidas_mes.get(r.producto_id, 0) + r.total

            products = (
                Product.query
                .filter(Product.deleted_at == None)
                .order_by(Product.codigo.asc())
                .all()
            )

            filas = []
            productos_con_movimiento = set(entradas_mes.keys()) | set(salidas_mes.keys())
            for p in products:
                pid = p.id
                precio_usd = float(p.precio_dolares or 0) * float(p.factor_ajuste or 1)
                # stock at end of month (reconstruct backwards from current)
                stock_cierre = p.stock - delta_after.get(pid, 0)
                # stock at start of month = cierre - net movement during month
                net_mes = entradas_mes.get(pid, 0) - salidas_mes.get(pid, 0)
                stock_apertura = stock_cierre - net_mes

                filas.append({
                    'codigo': p.codigo,
                    'descripcion': p.descripcion,
                    'proveedor': p.proveedor.nombre if p.proveedor else '',
                    'stock_apertura': max(0, stock_apertura),
                    'entradas': entradas_mes.get(pid, 0),
                    'salidas': salidas_mes.get(pid, 0),
                    'stock_cierre': max(0, stock_cierre),
                    'precio_usd': round(precio_usd, 2),
                    'valor_apertura_usd': round(max(0, stock_apertura) * precio_usd, 2),
                    'valor_cierre_usd': round(max(0, stock_cierre) * precio_usd, 2),
                    'valor_apertura_bs': round(max(0, stock_apertura) * precio_usd * exchange_rate, 2),
                    'valor_cierre_bs': round(max(0, stock_cierre) * precio_usd * exchange_rate, 2),
                })
            filas.sort(key=lambda x: x['codigo'])

            total_apertura_usd = round(sum(f['valor_apertura_usd'] for f in filas), 2)
            total_cierre_usd   = round(sum(f['valor_cierre_usd'] for f in filas), 2)
            total_apertura_bs  = round(sum(f['valor_apertura_bs'] for f in filas), 2)
            total_cierre_bs    = round(sum(f['valor_cierre_bs'] for f in filas), 2)
            total_entradas     = sum(f['entradas'] for f in filas)
            total_salidas      = sum(f['salidas'] for f in filas)

            return {
                'year': year,
                'month': month,
                'first_day': first_day,
                'last_day': last_day,
                'exchange_rate': exchange_rate,
                'filas': filas,
                'total_apertura_usd': total_apertura_usd,
                'total_cierre_usd': total_cierre_usd,
                'total_apertura_bs': total_apertura_bs,
                'total_cierre_bs': total_cierre_bs,
                'total_entradas': total_entradas,
                'total_salidas': total_salidas,
                'total_productos': len(filas),
                'productos_con_movimiento': len(productos_con_movimiento),
                'empresa': 'INVERSIONES FERRE-EXITO, C.A',
            }
        except Exception as e:
            current_app.logger.error(f"ReportsService.get_resumen_mensual error: {e}")
            return {
                'year': year, 'month': month,
                'first_day': date(year, month, 1),
                'last_day': date(year, month, 1),
                'exchange_rate': 1.0,
                'filas': [],
                'total_apertura_usd': 0, 'total_cierre_usd': 0,
                'total_apertura_bs': 0, 'total_cierre_bs': 0,
                'total_entradas': 0, 'total_salidas': 0,
                'total_productos': 0,
                'productos_con_movimiento': 0,
                'empresa': 'INVERSIONES FERRE-EXITO, C.A',
            }

