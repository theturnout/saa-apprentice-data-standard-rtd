'''
Parse tableschema to autogenerate documentation
'''
import re
import json
from pathlib import Path


def decorate_links(text, words):
    '''
    Adds rst-style references to words that appear in text

    Positional arguments:
    text -- text to be parsed for references
    words -- words to look for in the provided text
    '''
    regex = re.compile('(\\b(?:{})\\b)'.format('|'.join(words)))

    # based on http://www.saltycrane.com/blog/2007/10/using-pythons-finditer-to-highlight/
    i = 0
    output = ''
    for match in regex.finditer(text):
        output += ''.join(
            [
                text[i:match.start()],
                ':ref:`',
                text[match.start():match.end()],
                '`'
            ])
        i = match.end()

    return ''.join([output, text[i:]])


def create_docs(fields):
    '''
    Create rst documentation fragment from tableschema fields

    Positional arguments
    fields -- tableschema fields
    '''
    output_file = Path('source/schema/schema.rst.part')
    core_template = """{ref_label}

{name}
{name_header}

{data_type}\n
{example}\n
{description}\n
{enumerations}\n
{other_constraints}\n

"""
    data_type_reference_url_tmpl = 'https://specs.frictionlessdata.io/table-schema/#'
    field_names = [field['name'] for field in fields]
    data_types = list(set([field['type'] for field in fields]))

    with output_file.open('w') as rst:
        for field in fields:

            enumerations = ''
            other_constraints = ''

            if field.get("constraints"):
                if field['constraints'].get('enum'):
                    enumerations = 'The value of ``{}`` must be one of the following:\n\n'.format(
                        field['name'])
                    for enum in field['constraints']['enum']:
                        enumerations += '- {}\n'.format(enum)

                if field["constraints"].get('greaterThanField'):
                    other_constraints += 'The value of ``{}`` must be greater than the value of ``{}``'.format(
                        field['name'], field["constraints"]["greaterThanField"])

                for constraint, value in field.get("constraints").items():
                    if constraint not in ['enum', 'greaterThanField', 'pattern', 'minYearsBefore', 'maxYearsBefore']:
                        other_constraints += '- {}: {}\n'.format(
                            constraint.capitalize(), value)

            rst.write(core_template.format(
                ref_label='.. _{}:'.format(field['name']),
                name=field['name'],
                name_header='`' * len(field['name']),
                data_type=f'**Data Type:** `{field["type"]} <{
                    data_type_reference_url_tmpl}{field["type"]}>`_',
                example='**Example:** `{}`'.format(
                    field['example']) if 'example' in field else '',
                description=decorate_links(field['description'], field_names),
                enumerations=enumerations, other_constraints=other_constraints
            ))



def main():
    '''Starts the process of generating documentation'''
    tableschema = Path('./tableschema.json')

    if tableschema.exists():
        with tableschema.open() as data_file:
            data = json.loads(data_file.read())
            json_fields = [field for field in data['fields']]

            create_docs(json_fields)


if __name__ == '__main__':
    main()
