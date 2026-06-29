from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Auction, Item
from django import forms
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm class 'form-control' vào tất cả các trường
        for field in self.visible_fields():
            field.field.widget.attrs.update({'class': 'form-control'})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class AuctionCreateForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['start_price', 'start_time', 'end_time']
        widgets = {
            'start_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        start_price = cleaned_data.get("start_price")

        # Kiểm tra thời gian
        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("Thời gian kết thúc phải sau thời gian bắt đầu!")
        
        # Kiểm tra giá (nếu start_price là số âm)
        if start_price is not None and start_price < 0:
            raise forms.ValidationError("Giá khởi điểm không được là số âm!")

        return cleaned_data

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'image_url', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Giới hạn 2MB (2 * 1024 * 1024 bytes)
            max_size = 2 * 1024 * 1024
            if image.size > max_size:
                raise ValidationError("Ảnh quá lớn! Vui lòng chọn ảnh dưới 2MB.")
        return image