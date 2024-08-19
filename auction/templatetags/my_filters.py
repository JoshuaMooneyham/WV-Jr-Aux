from django import template

register = template.Library()

@register.filter(safe=True)
def moneyify(amt: int|float) -> str:
    amt /= 100
    return f'${amt:,.2f}'

@register.filter(safe=True)
def firstImg(images) -> str:
    try:
        for img in images:
            return img.file.url
    except:
        pass
    return ""

@register.filter(safe=True)
def indexify(image, images) -> str:
    return f'{images.index(image) + 1}/{len(images)}'

@register.filter(safe=True)
def getIndex(img, images) -> str:
    return f'{images.index(img) + 1}'

@register.filter(safe=True)
def countBids(bids):
    print(bids)

# register.filter('moneyify', moneyify)
# register.filter('firstImg', firstImg)
# register.filter('indexify', indexify)
