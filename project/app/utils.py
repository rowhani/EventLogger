import os
import uuid
import re
import jdatetime
from django.http import HttpResponse

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
    
def close_modal(reload_url = "/"):
    return HttpResponse("<script>window.location='%s';</script>" % reload_url)
    
def get_keywords(query):
    split_pattern = re.compile('("[^"]+"|\'[^\']+\'|\S+)')
    remove_inter_spaces_pattern = re.compile('[\s]{2,}')
    return [remove_inter_spaces_pattern.sub(' ', t.strip(' "\'')) for t in split_pattern.findall(query.strip()) if len(t.strip(' "\'')) > 0]
    
def get_truncated_text(sentence, keeped_words=[], suffix="...", boundry_letters_count=60):
    sentence = sentence.strip()
    try:
        if not keeped_words:
            width = boundry_letters_count * 2
            if len(sentence) <= width:
                return sentence
            else:
                if sentence[width].isspace():
                    return sentence[0:width] + suffix;
                else:
                    return sentence[0:width].rsplit(None, 1)[0] + suffix
        else:   
            ranges = []
            for kw in keeped_words:
                index = sentence.find(kw)
                if index != -1: ranges.append([max(index - boundry_letters_count, 0), min(index + boundry_letters_count, len(sentence))])
            ranges.sort(key=lambda r: r[0])

            if len(ranges) > 1:
                merged_ranges = []
                min_index, max_index = ranges[0]
                ranges = ranges[1:]
                for i, (min_r, max_r) in enumerate(ranges):
                    if min_r <= max_index:
                        max_index = max_r
                        if i == len(ranges) - 1: merged_ranges.append([min_index, max_index])
                    else:
                        merged_ranges.append([min_index, max_index])
                        min_index = min_r
                        max_index = max_r
            else:
                merged_ranges = ranges
                                         
            result = suffix if merged_ranges[0][0] != 0 else ''            
            for min_r, max_r in merged_ranges:
                if not sentence[min_r].isspace() and min_r > 0 and sentence[min_r - 1] != ' ':
                    mm = sentence[min_r:max_r].find(' ')
                    if mm != -1: min_r = min_r + mm + 1
                if not sentence[max_r].isspace() and max_r < len(sentence) - 1 and sentence[max_r + 1] != ' ':
                    mm = sentence[min_r:max_r].rfind(' ')
                    if mm != -1: max_r = min_r + mm
                result += sentence[min_r:max_r]
                if max_r != len(sentence): result += suffix
            return result
    except Exception, e:
        print "###", e
        return sentence
