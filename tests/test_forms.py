from forms import ProductoForm, ProveedorForm, MovimientoForm

def test_producto_form_valid(app_context):
    form = ProductoForm(data={
        'rubro': 'A',
        'iniciales': 'BC',
        'numero': '01',
        'descripcion': 'Producto Test',
        'stock': 10,
        'precio_dolares': 100.0,
        'factor_ajuste': 1.0
    })
    assert form.validate()

def test_producto_form_invalid(app_context):
    form = ProductoForm(data={
        'rubro': 'AB',  # Invalid
        'iniciales': 'B',  # Invalid
        'numero': '1',  # Invalid
        'descripcion': '',
        'stock': -1,  # Invalid
        'costo': -10.0,  # Invalid
        'factor_cambiario': 0  # Invalid
    })
    assert not form.validate()
    assert 'rubro' in form.errors
    assert 'stock' in form.errors

def test_proveedor_form_valid(app_context):
    form = ProveedorForm(data={
        'nombre': 'Proveedor Test',
        'rif': '123456789',
        'rubro_material': 'Material Test'
    })
    assert form.validate()

def test_movimiento_form_valid(app_context):
    form = MovimientoForm(data={
        'tipo': 'entrada',
        'producto_id': 1,
        'cantidad': 5
    })
    form.producto_id.choices = [(1, 'Producto Test')]
    assert form.validate()