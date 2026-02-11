from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class ProductoForm(FlaskForm):
    rubro = StringField('Rubro', validators=[DataRequired(), Length(min=1, max=1)])
    iniciales = StringField('Iniciales', validators=[DataRequired(), Length(min=2, max=2)])
    numero = StringField('Número', validators=[DataRequired(), Length(min=2, max=2)])
    descripcion = StringField('Descripción', validators=[DataRequired()])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    precio_dolares = FloatField('Precio en Dólares', validators=[DataRequired(), NumberRange(min=0)])
    factor_ajuste = FloatField('Factor de Ajuste', validators=[DataRequired(), NumberRange(min=0)])
    proveedor_id = SelectField('Proveedor', coerce=int, choices=[(0, 'Seleccionar')], validators=[Optional()])
    nuevo_proveedor = StringField('Nuevo Proveedor', validators=[Optional()])
    rif_nuevo = StringField('RIF Nuevo', validators=[Optional()])
    rubro_material_nuevo = StringField('Rubro Material Nuevo', validators=[Optional()])
    confirm_replace = BooleanField('Confirmar Reemplazo')
    submit = SubmitField('Crear Producto')

class ProveedorForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    rif = StringField('RIF', validators=[DataRequired()])
    rubro_material = StringField('Rubro Material', validators=[DataRequired()])
    submit = SubmitField('Crear Proveedor')

class MovimientoForm(FlaskForm):
    tipo = SelectField('Tipo', choices=[('entrada', 'Entrada'), ('salida', 'Salida')], validators=[DataRequired()])
    producto_id = SelectField('Producto', coerce=int, choices=[(0, 'Seleccionar')], validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    proveedor_id = SelectField('Proveedor', coerce=int, choices=[(0, 'Seleccionar')], validators=[Optional()])
    submit = SubmitField('Registrar Movimiento')

class ConfiguracionForm(FlaskForm):
    tasa_cambiaria = FloatField('Tasa Cambiaria (USD a VES)', validators=[DataRequired(), NumberRange(min=0)])
    factor_ajuste = FloatField('Factor de Ajuste', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Guardar Configuración')