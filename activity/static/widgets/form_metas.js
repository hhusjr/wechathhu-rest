function deepCopy(obj) {
    return JSON.parse(JSON.stringify(obj))
}

$(document).ready(function() {
    new Vue({
        el: '#form-metas-edit',
        data: {
            deleteFieldConfirmShow: {},
            activeNames: '',
            dialogVisible: false,
            sortFieldNames: '',
            typeTranslation: {
                'text': '单行文本框',
                'number': '数字框',
                'textarea': '多行文本域',
                'radio': '单选框',
                'checkbox': '多选框'
            },
            options: [
                { label: '单行文本框', type: 'text' },
                { label: '数字框', type: 'number' },
                { label: '多行文本域', type: 'textarea' },
                { label: '单选框', type: 'radio' },
                { label: '多选框', type: 'checkbox' },
            ],
            formMetasCode: '{}',
            type: '',
            attributes: {
                name: '',
                defaultText: '',
                required: false,
                choices: [{
                    'name': '',
                    'default': false
                }]
            },
            fields: {}
        },

        mounted() {
            this.formMetasCode = $('#form-metas-code').attr('data-initial')
            this.syncWithCode()
        },

        methods: {
            syncWithCode() {
                let code = this.formMetasCode
                let structure
                try {
                    structure = JSON.parse(code)
                } catch (e) {
                    return
                }
                let fields = {}
                for (let name in structure) {
                    let field = structure[name]
                    fields[name] = {}
                    if (!field.type) continue;
                    fields[name]['type'] = field.type
                    fields[name]['attributes'] = {
                        'name': name
                    }
                    fields[name]['attributes']['required'] = field.required ? true : false
                    if (field.type == 'text' || field.type == 'number' || field.type == 'textarea') {
                        fields[name]['attributes']['defaultText'] = field.default ? field.default : ''
                    } else if (field.type == 'radio' || field.type == 'checkbox') {
                        fields[name]['attributes']['choices'] = []
                        for (let choice of field.choices) {
                            let isDefault = field.default &&
                                ((field.type == 'radio' && field.default == choice) || (field.default.indexOf(choice) != -1))
                            fields[name]['attributes']['choices'].push({
                                default: isDefault,
                                name: choice
                            })
                        }
                    }
                }
                this.fields = deepCopy(fields)
            },

            changeCode() {
                this.syncWithCode()
            },

            refreshCode() {
                let fields = this.fields
                let formMetasObj = {}
                for (let name in fields) {
                    let fieldAttrs = {}
                    let field = fields[name]
                    fieldAttrs['type'] = field.type
                    fieldAttrs['required'] = field.attributes.required ? true : false
                    if (field.type == 'text' || field.type == 'textarea' || field.type == 'number') {
                        if (field.attributes.defaultText) fieldAttrs['default'] = field.attributes.defaultText
                    } else {
                        fieldAttrs['choices'] = []
                        let defaultChoices = []
                        for (let choice of field.attributes.choices) {
                            fieldAttrs['choices'].push(choice.name)
                            if (choice.default) defaultChoices.push(choice.name)
                        }
                        if (field.type == 'checkbox') fieldAttrs['default'] = defaultChoices
                        else if (defaultChoices[0]) fieldAttrs['default'] = defaultChoices[0]
                    }
                    formMetasObj[name] = fieldAttrs
                }
                this.formMetasCode = JSON.stringify(formMetasObj)
            },

            newField() {
                this.type = ''
                this.attributes = {
                    name: '',
                    choices: [{
                        'name': '',
                        'default': false
                    }]
                }
            },

            cleanField() {
                this.attributes = {
                    choices: [{
                        'name': '',
                        'default': false
                    }]
                }
            },

            deleteField(fieldName) {
                this.$delete(this.fields, fieldName)
                this.refreshCode()
            },

            editField(fieldName) {
                this.type = this.fields[fieldName].type
                this.attributes = deepCopy(this.fields[fieldName].attributes)
            },

            changeType() {
                if (this.type == 'radio') {
                    for (let i in this.attributes.choices) {
                        this.attributes.choices[i].default = false
                    }
                }
            },

            changeChoiceDefault(index) {
                if (this.type == 'checkbox' || !this.attributes.choices[index]) return
                for (let i in this.attributes.choices) {
                    this.attributes.choices[i].default = false
                }
                this.attributes.choices[index].default = true
            },

            saveField(formName) {
                this.$refs[formName].validate(valid => {
                    if (!valid) return false
                    let attributes = this.attributes
                    this.$set(this.fields, attributes.name, {
                        type: this.type,
                        attributes: attributes
                    })
                    this.newField()
                })
                this.refreshCode()
            },

            addChoice() {
                this.attributes.choices.push({
                    'name': '',
                    'default': false
                })
            },

            removeChoice(item) {
                let index = this.attributes.choices.indexOf(item)
                if (index !== -1) {
                    this.attributes.choices.splice(index, 1)
                }
            },
        }
    });
})