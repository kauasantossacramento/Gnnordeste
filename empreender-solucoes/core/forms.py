from django import forms

from .models import UFS, Candidatura, Mensagem, Proposta, Servico

MAX_CV = 5 * 1024 * 1024


class Honeypot(forms.Form):
    """Campo invisível: robôs preenchem, pessoas não."""

    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Envio inválido.")
        return ""


LGPD = "Concordo com o uso dos meus dados para retorno deste contato, conforme a Política de Privacidade."


class MensagemForm(Honeypot, forms.ModelForm):
    aceite = forms.BooleanField(label=LGPD)

    class Meta:
        model = Mensagem
        fields = ["nome", "email", "telefone", "assunto", "mensagem"]
        widgets = {
            "nome": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "telefone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel", "data-mask": "tel"}),
            "mensagem": forms.Textarea(attrs={"rows": 5}),
        }


class CandidaturaForm(Honeypot, forms.ModelForm):
    aceite = forms.BooleanField(label="Autorizo o tratamento dos meus dados para fins de recrutamento (LGPD).")

    class Meta:
        model = Candidatura
        fields = ["vaga", "nome", "email", "telefone", "cidade", "linkedin", "curriculo", "mensagem"]
        widgets = {
            "nome": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "telefone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel", "data-mask": "tel"}),
            "linkedin": forms.URLInput(attrs={"placeholder": "https://"}),
            "mensagem": forms.Textarea(attrs={"rows": 4}),
            "curriculo": forms.ClearableFileInput(attrs={"accept": ".pdf,.doc,.docx,.odt"}),
        }
        labels = {"mensagem": "Conte sobre sua experiência (opcional)", "cidade": "Cidade onde mora"}

    def __init__(self, *args, vagas=None, **kwargs):
        super().__init__(*args, **kwargs)
        if vagas is not None:
            self.fields["vaga"].queryset = vagas
        self.fields["vaga"].required = False
        self.fields["vaga"].empty_label = "Banco de talentos (todas as áreas)"
        self.fields["curriculo"].required = True

    def clean_curriculo(self):
        cv = self.cleaned_data.get("curriculo")
        if cv and cv.size > MAX_CV:
            raise forms.ValidationError("Envie um arquivo de até 5 MB.")
        return cv


class PropostaForm(Honeypot, forms.ModelForm):
    aceite = forms.BooleanField(label=LGPD)
    uf = forms.ChoiceField(label="UF", choices=[("", "UF")] + UFS)

    class Meta:
        model = Proposta
        fields = ["servicos", "perfis", "profissionais", "contrato", "inicio", "setor", "cidade", "uf",
                  "empresa", "nome", "cargo", "email", "telefone", "mensagem"]
        widgets = {
            "servicos": forms.CheckboxSelectMultiple,
            "perfis": forms.HiddenInput,
            "profissionais": forms.NumberInput(attrs={"min": 1, "max": 5000}),
            "contrato": forms.RadioSelect,
            "inicio": forms.RadioSelect,
            "setor": forms.RadioSelect,
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "telefone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel", "data-mask": "tel"}),
            "nome": forms.TextInput(attrs={"autocomplete": "name"}),
            "empresa": forms.TextInput(attrs={"autocomplete": "organization"}),
            "mensagem": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["servicos"].queryset = Servico.objects.filter(ativo=True)
        self.fields["servicos"].required = True
        self.fields["servicos"].error_messages["required"] = "Escolha pelo menos um serviço."


class AcompanharForm(forms.Form):
    protocolo = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"placeholder": "CV-2611-A1B2C3"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "E-mail usado na inscrição"}))
