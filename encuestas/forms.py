from django import forms

class SugerenciaForm(forms.Form):
    nombre = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    sugerencia = forms.CharField(widget=forms.Textarea, required=True)