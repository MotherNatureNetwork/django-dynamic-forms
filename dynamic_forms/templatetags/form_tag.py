from django import template
from django.utils.safestring import mark_safe
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
            <div id="form-thanks" style="display: none;">Thanks for your submission!</div>
            <script src="https://static.talesofthecocktail.com/js/vendor/jquery.js"></script>
            <script src="https://static.talesofthecocktail.com/js/validation/jquery.validate.min.js"></script>
            <script>
            $(window).on('load', function() {
              var xhr = new XMLHttpRequest(); 
              xhr.onreadystatechange = function () {
                  if (xhr.readyState === 4) {     
                      $('#form-insertion').html(xhr.responseText);
                      $("#dynamic-form").ajaxForm({url: '/dynamic_forms/forms/%s/', type: 'post', success:    function() { 
                          $('#form-insertion').html("");
                          $('#form-thanks').css('display', 'block');
                          $('#dynamic-form').validate();
                      }});
                  }   
              };      
              xhr.open('GET', '/dynamic_forms/forms/%s/');
              xhr.send();
            });
            </script>
        ''' % (form_id, form_id)
        safe = mark_safe(replace_string)
        body = body.replace(body[start_index-1:end_index+1], safe)
    return mark_safe(body)
