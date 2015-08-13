from django import template
register = template.Library()


@register.assignment_tag
def form_tag(body):
    """
    tag usage {% form_tag id %}
    """
    if '[totc-form' in body:
        start_index = body.find('totc-form id=')
        start_id_index = start_index + 13
        end_index = body.find(']', start_index)
        form_id = body[start_id_index:end_index]
        replace_string = '''
            <div id="form-insertion"></div>
            <script>
            var xhr = new XMLHttpRequest(); 
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {     
                    $('#form-insertion').html(xhr.responseText)
                }   
            };      
            xhr.open('GET', '/dynamic_forms/forms/%s/');
            xhr.send();
            </script>
        ''' % form_id
        body = body.replace(body[start_index-1:end_index+1], replace_string)
    return body
