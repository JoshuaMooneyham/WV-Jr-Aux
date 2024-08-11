from django import template

register = template.Library()

def moneyify(amt: int|float) -> str:
    amt /= 100
    return f'${amt:,.2f}'

def firstImg(images) -> str:
    try:
        for img in images:
            return img.file.url
    except:
        pass
    return ""

register.filter('moneyify', moneyify)
register.filter('firstImg', firstImg)