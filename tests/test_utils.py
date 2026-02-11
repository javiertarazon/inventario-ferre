from app import generar_codigo, generar_codigo_auto, _primeras_iniciales, _rubro_letra

def test_generar_codigo_valid():
    codigo, error = generar_codigo('A', 'BC', '01')
    assert codigo == 'A-BC-01'
    assert error is None

def test_generar_codigo_invalid_rubro():
    codigo, error = generar_codigo('AB', 'BC', '01')
    assert codigo is None
    assert error == 'El rubro debe ser 1 letra.'

def test_generar_codigo_invalid_iniciales():
    codigo, error = generar_codigo('A', 'B', '01')
    assert codigo is None
    assert error == 'Las iniciales deben ser 2 letras.'

def test_generar_codigo_invalid_numero():
    codigo, error = generar_codigo('A', 'BC', '1')
    assert codigo is None
    assert error == 'El número debe tener 2 dígitos.'

def test_primeras_iniciales():
    assert _primeras_iniciales('Producto Test') == 'PR'
    assert _primeras_iniciales('A') == 'AX'
    assert _primeras_iniciales('') == 'XX'

def test_rubro_letra():
    assert _rubro_letra('Categoria A') == 'C'
    assert _rubro_letra('123') == 'X'

def test_generar_codigo_auto(app_context):
    from models import Producto, db
    # Crear algunos productos para probar
    p1 = Producto(codigo='A-PT-01', descripcion='Producto Test')
    db.session.add(p1)
    db.session.commit()
    codigo, error = generar_codigo_auto('Categoria', 'Producto Nuevo')
    assert codigo == 'C-PR-01'
    assert error is None