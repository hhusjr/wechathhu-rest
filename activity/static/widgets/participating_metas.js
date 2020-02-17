$(document).ready(() => {
    $('#enrollment_form').submit(() => {
        let data = {}
        $('.form-metas').each(function() {
            let self = $(this)
            let type = self.attr('data-type')
            let name = self.attr('data-name')
            switch (type) {
                case 'text':
                case 'number':
                case 'textarea':
                    data[name] = self.val()
                    break;
                case 'radio':
                    data[name] = self.find('option:selected').val()
                    break;
                case 'checkbox':
                    let chosen = []
                    self.find('option:selected').each(function() {
                        chosen.push($(this).val())
                    })
                    data[name] = chosen
                    break;
            }
        })
        $('#participating_metas').val(JSON.stringify(data))
        return true
    })
})