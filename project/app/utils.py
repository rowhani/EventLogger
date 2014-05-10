import os
import uuid
import jdatetime

def validate_jalali_date(form, cleaned_data, field, check_required=False):
    prefix_field = "%s-%s" % (form.prefix, field) if form.prefix else field
    dt = form.data.get(prefix_field, None)
    if field in form._errors: del form._errors[field]
    if not dt:
        if check_required:
            form._errors[field] = "این فیلد لازم است."
    else:
        try: cleaned_data[field] = jdatetime.datetime.strptime(dt, '%Y/%m/%d').togregorian()
        except: form._errors[field] = "یک تاریخ/زمان معتبر وارد کنید."
        
def validate_image(form, cleaned_data, field):
    prefix_field = "%s-%s" % (form.prefix, field) if form.prefix else field
    image = form.files.get(prefix_field, None)
    if image:
        if not image.content_type.startswith('image'):
            form._errors[field] = ['تصویر معتبر نیست.']
        else:
            cleaned_data[field] = image.name
    elif form.instance:
        cleaned_data[field] = getattr(form.instance, field)
        
def save_request_file(destination, request_file):
    ext = os.path.splitext(request_file.name)[1]
    name =  "%s%s" % (uuid.uuid4(), ext)
    path = "%s/%s" % (destination, name)
    with open(path, 'wb+') as f:
        for chunk in request_file.chunks(): f.write(chunk) 
    return name