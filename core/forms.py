from django import forms

from .models import Candidatura, Denuncia, MensagemContato

MAX_CV = 5 * 1024 * 1024


class HoneypotMixin(forms.Form):
    """Campo invisível: robôs preenchem, pessoas não."""

    site = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "tabindex": "-1", "autocomplete": "off", "class": "hp"}))

    def clean_site(self):
        if self.cleaned_data.get("site"):
            raise forms.ValidationError("Envio inválido.")
        return ""


class ContatoForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = MensagemContato
        fields = ["nome", "email", "telefone", "assunto", "mensagem"]
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Seu nome", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Seu e-mail", "autocomplete": "email"}),
            "telefone": forms.TextInput(attrs={"placeholder": "Telefone / WhatsApp", "autocomplete": "tel"}),
            "assunto": forms.TextInput(attrs={"placeholder": "Assunto (ex.: orçamento)"}),
            "mensagem": forms.Textarea(attrs={"placeholder": "Escreva sua mensagem…", "rows": 5}),
        }


class CandidaturaForm(HoneypotMixin, forms.ModelForm):
    aceite = forms.BooleanField(
        label="Autorizo o uso dos meus dados para fins de recrutamento (LGPD).", required=True)

    class Meta:
        model = Candidatura
        fields = ["vaga", "nome", "email", "telefone", "cidade", "curriculo", "mensagem"]
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Nome completo", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "E-mail", "autocomplete": "email"}),
            "telefone": forms.TextInput(attrs={"placeholder": "Telefone / WhatsApp", "autocomplete": "tel"}),
            "cidade": forms.TextInput(attrs={"placeholder": "Cidade onde mora"}),
            "mensagem": forms.Textarea(attrs={"placeholder": "Conte um pouco sobre sua experiência (opcional)", "rows": 4}),
            "curriculo": forms.ClearableFileInput(attrs={"accept": ".pdf,.doc,.docx,.odt"}),
        }

    def __init__(self, *args, vagas=None, **kwargs):
        super().__init__(*args, **kwargs)
        if vagas is not None:
            self.fields["vaga"].queryset = vagas
        self.fields["vaga"].required = False
        self.fields["vaga"].empty_label = "Banco de talentos (qualquer vaga)"

    def clean_curriculo(self):
        cv = self.cleaned_data.get("curriculo")
        if cv and cv.size > MAX_CV:
            raise forms.ValidationError("O arquivo deve ter no máximo 5 MB.")
        return cv


class DenunciaForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = Denuncia
        fields = ["categoria", "relato", "anonima", "nome", "contato"]
        widgets = {
            "relato": forms.Textarea(attrs={"rows": 6, "placeholder": "Descreva o ocorrido com o máximo de detalhes: o quê, onde, quando e quem."}),
            "nome": forms.TextInput(attrs={"placeholder": "Seu nome (opcional)"}),
            "contato": forms.TextInput(attrs={"placeholder": "E-mail ou telefone (opcional)"}),
        }
        labels = {"anonima": "Quero fazer a denúncia de forma anônima"}

    def clean(self):
        data = super().clean()
        if data.get("anonima"):
            data["nome"] = ""
            data["contato"] = ""
        return data


class ProtocoloForm(forms.Form):
    protocolo = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"placeholder": "Ex.: 202611-A1B2C3"}))
