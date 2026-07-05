from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    
    def validate(self, password, user=None):
        if all((
            re.search('[0-9]', password),
            re.search('[a-zA-Z]', password),
        )):
            return
        raise ValidationError('パスワードには、英数字を含めてください。')
    
    def get_help_text(self):
        return 'パスワードには、10文字以上・英数字を含めてください。'