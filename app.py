from flask import Flask, render_template, request, redirect, url_for, flash, abort
from models import db, Producto, Proveedor, Movimiento, CierreDia, Usuario, Configuracion
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import ProductoForm, ProveedorForm, MovimientoForm, ConfiguracionForm
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from datetime import datetime
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///inventario.db')
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ... todas las rutas y lógica existentes ...

# --- RUTA DE EDICIÓN DE PRODUCTO ---
@app.route('/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
@login_required
def editar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    form = ProductoForm(obj=producto)
    form.proveedor_id.choices = [(0, 'Seleccionar existente')] + [(p.id, p.nombre) for p in Proveedor.query.all()]
    if form.validate_on_submit():
        producto.codigo = generar_codigo(form.rubro.data, form.iniciales.data, form.numero.data)[0]
        producto.descripcion = form.descripcion.data
        producto.stock = form.stock.data
        producto.precio_dolares = form.precio_dolares.data
        producto.factor_ajuste = form.factor_ajuste.data
        producto.proveedor_id = form.proveedor_id.data if form.proveedor_id.data != 0 else None
        db.session.commit()
        flash('Producto editado correctamente.')
        return redirect(url_for('productos'))
    return render_template('productos.html', productos=Producto.query.paginate(page=1, per_page=10), proveedores=Proveedor.query.all(), rubros={}, form=form, config=Configuracion.query.first(), editando=True, producto_edit=producto)
# --- FIN RUTA DE EDICIÓN ---
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from models import db, Producto, Proveedor, Movimiento, CierreDia, Usuario, Configuracion
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import ProductoForm, ProveedorForm, MovimientoForm, ConfiguracionForm
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from datetime import datetime
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///inventario.db')
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ...existing code...

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from models import db, Producto, Proveedor, Movimiento, CierreDia, Usuario, Configuracion
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import ProductoForm, ProveedorForm, MovimientoForm, ConfiguracionForm
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from datetime import datetime
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///inventario.db')
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

def generar_codigo(rubro, iniciales, numero):
    rubro = (rubro or '').strip().upper()
    iniciales = (iniciales or '').strip().upper()
    numero = (numero or '').strip()
    if len(rubro) != 1 or not rubro.isalpha():
        return None, 'El rubro debe ser 1 letra.'
    if len(iniciales) != 2 or not iniciales.isalpha():
        return None, 'Las iniciales deben ser 2 letras.'
    if len(numero) != 2 or not numero.isdigit():
        return None, 'El número debe tener 2 dígitos.'

    codigo = f"{rubro}-{iniciales}-{numero}"
    return codigo, None

def _primeras_iniciales(descripcion):
    texto = (descripcion or '').strip().upper()
    letras = [c for c in texto if c.isalpha()]
    if len(letras) >= 2:
        return ''.join(letras[:2])
    if len(letras) == 1:
        return letras[0] + 'X'
    return 'XX'

def _rubro_letra(categoria):
    texto = (categoria or '').strip().upper()
    for c in texto:
        if c.isalpha():
            return c
    return 'X'

def generar_codigo_auto(categoria, descripcion):
    rubro = _rubro_letra(categoria)
    iniciales = _primeras_iniciales(descripcion)
    prefijo = f"{rubro}-{iniciales}-"
    existentes = Producto.query.filter(Producto.codigo.like(f"{prefijo}%")).all()
    max_num = 0
    for p in existentes:
        try:
            num = int(p.codigo.split('-')[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            continue
    siguiente = max_num + 1
    if siguiente > 99:
        return None, 'Se alcanzó el límite de 99 códigos para ese prefijo.'
    codigo = f"{rubro}-{iniciales}-{siguiente:02d}"
    return codigo, None

@app.route('/')
@login_required
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Usuario.query.filter_by(username=username).first()
        if user and (check_password_hash(user.password, password) if not app.config['TESTING'] else user.password == password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Credenciales inválidas')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    config = Configuracion.query.first()
    if not config:
        config = Configuracion(tasa_cambiaria=1.0, factor_ajuste=1.0)
        db.session.add(config)
        db.session.commit()
    form = ConfiguracionForm(obj=config)
    if form.validate_on_submit():
        config.tasa_cambiaria = form.tasa_cambiaria.data
        config.factor_ajuste = form.factor_ajuste.data
        db.session.commit()
        flash('Configuración guardada.')
        return redirect(url_for('configuracion'))
    return render_template('configuracion.html', form=form)

@app.route('/productos', methods=['GET', 'POST'])
@login_required
def productos():
    page = request.args.get('page', 1, type=int)
    form = ProductoForm()
    form.proveedor_id.choices = [(0, 'Seleccionar existente')] + [(p.id, p.nombre) for p in Proveedor.query.all()]
    if form.validate_on_submit():
        rubro = form.rubro.data
        iniciales = form.iniciales.data
        numero = form.numero.data
        descripcion = form.descripcion.data
        stock = form.stock.data
        precio_dolares = form.precio_dolares.data
        factor_ajuste = form.factor_ajuste.data
        proveedor_id = form.proveedor_id.data if form.proveedor_id.data != 0 else None
        nuevo_proveedor = form.nuevo_proveedor.data
        codigo, error = generar_codigo(rubro, iniciales, numero)
        if error:
            flash(error)
            return redirect(url_for('productos'))
        existente = Producto.query.filter_by(codigo=codigo).first()
        if existente and not form.confirm_replace.data:
            productos = Producto.query.all()
            proveedores = Proveedor.query.all()
            return render_template(
                'productos.html',
                productos=productos,
                proveedores=proveedores,
                confirmar_reemplazo=True,
                codigo_reemplazo=codigo,
                existente=existente,
                form=form
            )
        try:
            if nuevo_proveedor:
                rif_nuevo = form.rif_nuevo.data
                rubro_material_nuevo = form.rubro_material_nuevo.data
                proveedor = Proveedor(nombre=nuevo_proveedor, rif=rif_nuevo, rubro_material=rubro_material_nuevo)
                db.session.add(proveedor)
                db.session.commit()
                proveedor_id = proveedor.id
            if existente:
                existente.descripcion = descripcion
                existente.stock = stock
                existente.precio_dolares = precio_dolares
                existente.factor_ajuste = factor_ajuste
                existente.proveedor_id = proveedor_id
                db.session.commit()
                flash(f'Producto actualizado con código {codigo}')
            else:
                producto = Producto(
                    codigo=codigo,
                    descripcion=descripcion,
                    stock=stock,
                    precio_dolares=precio_dolares,
                    factor_ajuste=factor_ajuste,
                    proveedor_id=proveedor_id
                )
                db.session.add(producto)
                db.session.commit()
                flash(f'Producto creado con código {codigo}')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Error en productos: {e}')
            flash('Error al procesar el producto.')
        return redirect(url_for('productos'))
    productos = Producto.query.paginate(page=page, per_page=10, error_out=False)
    proveedores = Proveedor.query.all()
    config = Configuracion.query.first()
    if not config:
        config = Configuracion(tasa_cambiaria=1.0, factor_ajuste=1.0)
        db.session.add(config)
        db.session.commit()
    rubros = {}
    for p in productos.items:
        if p.codigo and '-' in p.codigo:
            rubro = p.codigo.split('-')[0]
        else:
            rubro = 'SIN'
        rubros.setdefault(rubro, []).append(p)
    return render_template('productos.html', productos=productos, proveedores=proveedores, rubros=rubros, form=form, config=config)

@app.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    if request.method == 'POST':
        nombre = request.form['nombre']
        rif = request.form['rif']
        rubro_material = request.form['rubro_material']
        proveedor = Proveedor(nombre=nombre, rif=rif, rubro_material=rubro_material)
        db.session.add(proveedor)
        db.session.commit()
        flash('Proveedor creado')
        return redirect(url_for('proveedores'))
    proveedores = Proveedor.query.all()
    return render_template('proveedores.html', proveedores=proveedores)

@app.route('/movimientos', methods=['GET', 'POST'])
def movimientos():
    if request.method == 'POST':
        try:
            tipo = request.form['tipo']
            producto_id = int(request.form['producto_id'])
            cantidad = int(request.form['cantidad'])
            fecha = datetime.now()
            proveedor_id = request.form.get('proveedor_id')
            if proveedor_id:
                proveedor_id = int(proveedor_id)
            movimiento = Movimiento(tipo=tipo, producto_id=producto_id, cantidad=cantidad, fecha=fecha, proveedor_id=proveedor_id)
            producto = db.session.get(Producto, producto_id)
            if not producto:
                flash('Producto no encontrado.')
                return redirect(url_for('movimientos'))
            if tipo == 'entrada':
                producto.stock += cantidad
            else:
                if producto.stock < cantidad:
                    flash('Stock insuficiente para salida.')
                    return redirect(url_for('movimientos'))
                producto.stock -= cantidad
            db.session.add(movimiento)
            db.session.commit()
            flash('Movimiento registrado')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Error en movimientos: {e}')
            flash('Error al registrar movimiento.')
        return redirect(url_for('movimientos'))
    productos = Producto.query.all()
    proveedores = Proveedor.query.all()
    fecha_str = request.args.get('fecha')
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha = datetime.now().date()
    else:
        fecha = datetime.now().date()
    movimientos = Movimiento.query.filter(db.func.date(Movimiento.fecha) == fecha).order_by(Movimiento.fecha).all()
    cierre = CierreDia.query.filter_by(fecha=fecha).first()
    cierres = CierreDia.query.order_by(CierreDia.fecha.desc()).all()
    return render_template(
        'movimientos.html',
        productos=productos,
        proveedores=proveedores,
        movimientos=movimientos,
        fecha=fecha,
        cierre=cierre,
        cierres=cierres
    )

@app.route('/cerrar_dia', methods=['POST'])
def cerrar_dia():
    fecha_str = request.form.get('fecha')
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        fecha = datetime.now().date()

    cierre_existente = CierreDia.query.filter_by(fecha=fecha).first()
    if cierre_existente:
        flash('El día ya está cerrado.')
        return redirect(url_for('movimientos', fecha=fecha.strftime('%Y-%m-%d')))

    movimientos_dia = Movimiento.query.filter(db.func.date(Movimiento.fecha) == fecha).all()
    for m in movimientos_dia:
        m.cerrado = True

    cierre = CierreDia(fecha=fecha, cerrado_en=datetime.now())
    db.session.add(cierre)
    db.session.commit()
    flash('Día cerrado y guardado.')
    return redirect(url_for('movimientos', fecha=fecha.strftime('%Y-%m-%d')))

@app.route('/exportar_dia')
def exportar_dia():
    fecha_str = request.args.get('fecha')
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        fecha = datetime.now().date()

    movimientos = Movimiento.query.filter(db.func.date(Movimiento.fecha) == fecha).order_by(Movimiento.fecha).all()
    data = []
    for m in movimientos:
        precio_dolares = m.producto.precio_dolares if m.producto.precio_dolares is not None else 0.0
        factor_ajuste = m.producto.factor_ajuste if m.producto.factor_ajuste is not None else 1.0
        row = {
            'Fecha': m.fecha.strftime('%Y-%m-%d'),
            'Código Producto': m.producto.codigo,
            'Descripción': m.producto.descripcion,
            'Entrada': m.cantidad if m.tipo == 'entrada' else 0,
            'Salida': m.cantidad if m.tipo == 'salida' else 0,
            'Stock Actual': m.producto.stock,
            'Precio en Dólares': precio_dolares,
            'Factor de Ajuste': factor_ajuste,
            'Precio Ajustado': round(precio_dolares * factor_ajuste, 2),
            'Proveedor': m.proveedor.nombre if m.proveedor else ''
        }
        data.append(row)

    df = pd.DataFrame(data)
    filename = f"inventario_diario_{fecha.strftime('%Y-%m-%d')}.xlsx"
    output_path = os.path.join(os.getcwd(), filename)
    df.to_excel(output_path, index=False)
    flash(f'Exportado: {filename}')
    return redirect(url_for('movimientos', fecha=fecha.strftime('%Y-%m-%d')))

@app.route('/exportar_inventario_completo')
def exportar_inventario_completo():
    productos = Producto.query.filter(Producto.codigo.isnot(None)).order_by(Producto.codigo).all()
    config = Configuracion.query.first()
    if not config:
        config = Configuracion(tasa_cambiaria=1.0, factor_ajuste=1.0)
    data = []
    for p in productos:
        precio_dolares = p.precio_dolares if p.precio_dolares is not None else 0.0
        precio_bolivares = round(precio_dolares * config.tasa_cambiaria, 2)
        precio_ajustado = round(precio_bolivares * p.factor_ajuste, 2)
        row = {
            'Código Producto': p.codigo,
            'Descripción': p.descripcion,
            'Stock': p.stock,
            'Precio en Dólares': precio_dolares,
            'Precio en Bolívares': precio_bolivares,
            'Precio Ajustado': precio_ajustado,
            'Proveedor': p.proveedor.nombre if p.proveedor else ''
        }
        data.append(row)

    df = pd.DataFrame(data)
    filename = f"inventario_completo_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    output_path = os.path.join(os.getcwd(), filename)
    df.to_excel(output_path, index=False)
    flash(f'Exportado: {filename}')
    return redirect(url_for('inventario', view='completo'))

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        rubro = request.form.get('rubro', '').strip().upper()
        criterio = request.form.get('criterio', 'descripcion')
        q = Producto.query
        if rubro:
            q = q.filter(Producto.codigo.like(f"{rubro}-%"))
        if query:
            if criterio == 'codigo':
                q = q.filter(Producto.codigo.contains(query))
            else:
                q = q.filter(Producto.descripcion.ilike(f"{query}%"))
        productos = q.all()
        return render_template('buscar.html', productos=productos, query=query, rubro=rubro, criterio=criterio)
    return render_template('buscar.html')

@app.route('/inventario')
def inventario():
    view = request.args.get('view', 'completo')
    reset = request.args.get('reset') == '1'
    fecha = None
    fecha_especifica = None

    if view == 'diario' and not reset:
        # Primero buscar por fecha guardada (del select dropdown)
        fecha_str = request.args.get('fecha')
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                fecha = None

        # Si no hay fecha guardada, buscar por fecha específica (ingresada)
        if not fecha:
            fecha_especifica_str = request.args.get('fecha_especifica')
            if fecha_especifica_str:
                try:
                    fecha = datetime.strptime(fecha_especifica_str, '%Y-%m-%d').date()
                    fecha_especifica = fecha_especifica_str
                except ValueError:
                    fecha = None

        if fecha:
            movimientos = Movimiento.query.filter(db.func.date(Movimiento.fecha) == fecha).order_by(Movimiento.fecha).all()
        else:
            movimientos = []
        productos = []
    else:
        view = 'completo'
        movimientos = []
        productos = Producto.query.filter(Producto.codigo.isnot(None)).order_by(Producto.codigo).all()

    tiene_movimientos = bool(movimientos)
    tiene_productos = bool(productos)
    fechas_disponibles = CierreDia.query.order_by(CierreDia.fecha.desc()).all()
    return render_template(
        'inventario_diario.html',
        movimientos=movimientos,
        productos=productos,
        fecha=fecha,
        fecha_especifica=fecha_especifica,
        fechas_disponibles=fechas_disponibles,
        view=view,
        tiene_movimientos=tiene_movimientos,
        tiene_productos=tiene_productos
    )

@app.route('/inventario_diario')
def inventario_diario():
    return redirect(url_for('inventario'))

@app.route('/importar_excel', methods=['POST'])
def importar_excel():
    try:
        ruta = 'Inventario Ferre-Exito.xlsx'
        if not os.path.exists(ruta):
            flash('Archivo Excel no encontrado.')
            return redirect(url_for('productos'))
        df = pd.read_excel(ruta, sheet_name='Inventario Costo Producto', header=2)
    except Exception as e:
        logging.error(f'Error al leer Excel: {e}')
        flash(f'Error al procesar Excel: {str(e)}')
        return redirect(url_for('productos'))

    creados = 0
    actualizados = 0
    omitidos = 0

    try:
        for _, row in df.iterrows():
            categoria = row.get('Categoria')
            descripcion = row.get('Descripcion del Articulo')
            if not descripcion or str(descripcion).strip() == 'nan':
                omitidos += 1
                continue
            cantidad = row.get('Cantidad Unid/kg') or 0
            costo_unit = row.get('Costo Unit $') or 0

            codigo, error = generar_codigo_auto(categoria, descripcion)
            if error:
                omitidos += 1
                continue

            existente = Producto.query.filter_by(codigo=codigo).first()
            if existente:
                existente.descripcion = str(descripcion)
                existente.stock = int(float(cantidad)) if str(cantidad).strip() else 0
                existente.precio_dolares = float(costo_unit) if str(costo_unit).strip() else 0.0
                existente.factor_ajuste = existente.factor_ajuste or 1.0
                actualizados += 1
            else:
                producto = Producto(
                    codigo=codigo,
                    descripcion=str(descripcion),
                    stock=int(float(cantidad)) if str(cantidad).strip() else 0,
                    precio_dolares=float(costo_unit) if str(costo_unit).strip() else 0.0,
                    factor_ajuste=1.0
                )
                db.session.add(producto)
                creados += 1

        db.session.commit()
        flash(f'Importación completada. Creados: {creados}, actualizados: {actualizados}, omitidos: {omitidos}.')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error en importación: {e}')
        flash('Error durante la importación.')
    return redirect(url_for('productos'))

@app.route('/exportar', methods=['GET', 'POST'])
def exportar():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        if tipo == 'diario':
            fecha_str = request.form.get('fecha')
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                fecha = datetime.now().date()
            return redirect(url_for('exportar_dia', fecha=fecha.strftime('%Y-%m-%d')))

        movimientos = Movimiento.query.all()
        data = []
        for m in movimientos:
            precio_dolares = m.producto.precio_dolares if m.producto.precio_dolares is not None else 0.0
            factor_ajuste = m.producto.factor_ajuste if m.producto.factor_ajuste is not None else 1.0
            row = {
                'Fecha': m.fecha.strftime('%Y-%m-%d'),
                'Código Producto': m.producto.codigo,
                'Descripción': m.producto.descripcion,
                'Stock Actual': m.producto.stock,
                'Precio en Dólares': precio_dolares,
                'Factor de Ajuste': factor_ajuste,
                'Precio Ajustado': round(precio_dolares * factor_ajuste, 2),
                'Proveedor': m.proveedor.nombre if m.proveedor else ''
            }
            if m.tipo == 'entrada':
                row['Entrada'] = m.cantidad
                row['Salida'] = 0
            else:
                row['Entrada'] = 0
                row['Salida'] = m.cantidad
            data.append(row)
        df = pd.DataFrame(data)
        df.to_excel('inventario_exportado.xlsx', index=False)
        flash('Exportado a inventario_exportado.xlsx')
        return redirect(url_for('exportar'))

    return render_template('exportar.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Usuario.query.first():
            usuario = Usuario(username='admin', password=generate_password_hash('admin'))
            db.session.add(usuario)
            db.session.commit()
    app.run(debug=True, use_reloader=False)