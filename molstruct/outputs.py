#!/usr/bin/env python
import datetime
import html
import json
import uuid

import molstruct.names as n


def jsonldhtml(reader, limit):
    print('''<!DOCTYPE html>
    <html lang="en">
      <head>
        <title>Example Document</title>
        <script type="application/ld+json">''')
    jsonld(reader, limit)
    print('''        </script>
      </head>
    </html>''')


def jsonld(reader, limit):
    i = 0

    out_str = '{\n'
    out_str += '  "@graph" : [\n'
    out_str += '''    {
      "@id": "https://github.com/lszeremeta/molstruct",
      "@type": "http://schema.org/Organization",
      "http://schema.org/name": "Molstruct"
    },
    {
      "@id": "#",
      "@type": "http://schema.org/Dataset",
      "http://schema.org/about": {
        "@id": "https://github.com/lszeremeta/molstruct"
      },
      "http://schema.org/description": "This is a dataset of molecules generated by Molstruct.",
      "http://schema.org/keywords": [
        "molecules",
        "cheminformatics",
        "chemical compounds"
      ],
      "http://schema.org/license": {
        "@id": "http://opendatacommons.org/licenses/pddl/1.0/"
      },
      "http://schema.org/name": "Molecules",
      "http://schema.org/creator": {
        "@id": "https://github.com/lszeremeta/molstruct"
      },
      "http://schema.org/temporal": "''' + str(datetime.datetime.today().year) + '''",
      "http://schema.org/url": "https://github.com/lszeremeta/molstruct"
    },'''
    for row in reader:
        out_str += '\n    {\n'

        if n.SUBJECT_BASE:
            out_str += '      "@id" : ' + json.dumps(n.SUBJECT_BASE + str(i))
        else:
            out_str += '      "@id" : ' + json.dumps('urn:uuid:' + str(uuid.uuid4()))

        out_str += ',\n      "@type" : "https://schema.org/MolecularEntity",\n'

        for key, value in n.COLUMNS.items():
            if n.VALUE_DELIMITER in str(row.get(value)):
                out_str += '      "' + key + '" : ' + json.dumps(row.get(value).split(n.VALUE_DELIMITER)) + ',\n'
            elif row.get(value):
                out_str += '      "' + key + '" : ' + json.dumps(row.get(value)) + ',\n'

        out_str = out_str[:-2] + '\n'
        out_str += '    },'

        if i == limit:
            break

        i = i + 1
    out_str = out_str[:-1]

    print(out_str + '''\n  ],
  "@context" : {
    "identifier" : {
      "@id" : "https://schema.org/identifier"
    },
    "name" : {
      "@id" : "https://schema.org/name"
    },
    "inChIKey" : {
      "@id" : "https://schema.org/inChIKey"
    },
    "inChI" : {
      "@id" : "https://schema.org/inChI"
    },
    "smiles" : {
      "@id" : "https://schema.org/smiles"
    },
    "url" : {
      "@id" : "https://schema.org/url"
    },
    "iupacName" : {
      "@id" : "https://schema.org/iupacName"
    },
    "molecularFormula" : {
      "@id" : "https://schema.org/molecularFormula"
    },
    "molecularWeight" : {
      "@id" : "https://schema.org/molecularWeight"
    },
    "monoisotopicMolecularWeight" : {
      "@id" : "https://schema.org/monoisotopicMolecularWeight"
    },
    "description" : {
      "@id" : "https://schema.org/description"
    },
    "disambiguatingDescription" : {
      "@id" : "https://schema.org/disambiguatingDescription"
    },
    "image" : {
      "@id" : "https://schema.org/image"
    },
    "alternateName" : {
      "@id" : "https://schema.org/alternateName"
    },
    "sameAs" : {
      "@id" : "https://schema.org/sameAs"
    },
    "schema" : "https://schema.org/"
  }
}''')


def rdfa(reader, limit):
    i = 0
    print('''<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Example Document</title>
  </head>
  <body vocab="http://schema.org/">
    <div typeof="schema:Dataset">
      <div rel="schema:creator">
        <div typeof="schema:Organization" about="https://github.com/lszeremeta/molstruct">
          <div property="schema:name" content="Molstruct"></div>
        </div>
      </div>
      <div property="schema:keywords" content="cheminformatics"></div>
      <div property="schema:keywords" content="molecules"></div>
      <div property="schema:keywords" content="chemical compounds"></div>
      <div property="schema:temporal" content="''' + str(datetime.datetime.today().year) + '''"></div>
      <div property="schema:name" content="Molecules"></div>
      <div rel="schema:license" resource="http://opendatacommons.org/licenses/pddl/1.0/"></div>
      <div property="schema:description" content="This is a dataset of molecules generated by Molstruct."></div>
      <div rel="schema:about" resource="https://github.com/lszeremeta/molstruct"></div>
      <div property="schema:url" content="https://github.com/lszeremeta/molstruct"></div>
    </div>''')
    for row in reader:
        if n.SUBJECT_BASE:
            print('    <div typeof="schema:MolecularEntity" about="' + html.escape(n.SUBJECT_BASE + str(
                i), quote=True), end='')

            if '#' in n.SUBJECT_BASE:
                print('" id="' + html.escape(n.SUBJECT_BASE.rpartition('#')[-1] + str(i), quote=True), end='')

        else:
            print('    <div typeof="schema:MolecularEntity" about="urn:uuid:' + str(uuid.uuid4()), end='')

        print('">')

        for key, value in n.COLUMNS.items():
            if row.get(value):
                values = row.get(value).split(n.VALUE_DELIMITER)
                for v in values:
                    if key == 'url' or key == 'sameAs':
                        print('      <a href="' + html.escape(v,
                                                              quote=True) + '" rel="schema:' + key + '">' + html.escape(
                            v) + '</a>')
                    elif key == 'image':
                        print('      <img src="' + html.escape(v, quote=True) + '" alt="Image of the Molecule' + str(
                            i) + '" rel="schema:' + key + '">')
                    else:
                        print('      <div property="schema:' + key + '">' + html.escape(v) + '</div>')

        print('    </div>')

        if i == limit:
            break

        i = i + 1
    print('  </body>')
    print('</html>')


def microdata(reader, limit):
    i = 0
    print('''<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Example Document</title>
  </head>
  <body>
    <div itemscope itemtype="https://schema.org/Dataset">
      <div itemprop="name" content="Molecules"></div>
      <div itemprop="keywords" content="cheminformatics"></div>
      <div itemprop="keywords" content="molecules"></div>
      <div itemprop="keywords" content="chemical compounds"></div>
      <div itemprop="temporal" content="''' + str(datetime.datetime.today().year) + '''"></div>
      <div itemprop="url" content="https://github.com/lszeremeta/molstruct"></div>
      <div itemprop="description" content="This is a dataset of molecules generated by Molstruct."></div>
      <div itemprop="creator" itemscope itemtype="https://schema.org/Organization">
        <div itemprop="name" content="Molstruct"></div>
      </div>
      <div itemprop="license" content="http://opendatacommons.org/licenses/pddl/1.0/"></div>
    </div>''')
    for row in reader:
        if n.SUBJECT_BASE:
            print('    <div itemscope itemtype="http://schema.org/MolecularEntity" itemid="' + html.escape(
                n.SUBJECT_BASE + str(
                    i), quote=True), end='')

            if '#' in n.SUBJECT_BASE:
                print('" id="' + html.escape(n.SUBJECT_BASE.rpartition('#')[-1] + str(i), quote=True), end='')
        else:
            print(
                '    <div itemscope itemtype="http://schema.org/MolecularEntity" itemid="urn:uuid:' + str(uuid.uuid4()),
                end='')

        print('">')

        for key, value in n.COLUMNS.items():
            if row.get(value):
                values = row.get(value).split(n.VALUE_DELIMITER)
                for v in values:
                    if key == 'url' or key == 'sameAs':
                        print(
                            '      <a href="' + html.escape(v, quote=True) + '" itemprop="' + key + '">' + html.escape(
                                v) + '</a>')
                    elif key == 'image':
                        print('      <img src="' + html.escape(v, quote=True) + '" alt="Image of the Molecule' + str(
                            i) + '" itemprop="' + key + '">')
                    else:
                        print('      <div itemprop="' + key + '">' + html.escape(v) + '</div>')

        print('    </div>')

        if i == limit:
            break

        i = i + 1
    print('  </body>')
    print('</html>')
