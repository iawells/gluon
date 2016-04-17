#!/usr/bin/python
from __future__ import print_function
import sys
import re
import yaml
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


class ModelProcessor(object):
    def __init__(self, *models):
        self.data={}
        for model in models:
            self.add_model(model)

    def add_model(model):
            self.data.update(yaml.safe_load(model))

    def sqla_models(self, base=None):
        """Make SQLAlchemy classes for each of the elements in the data read"""

        if base == None:
            base = declarative_base()

        def de_camel(s):
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


        # Make a model class that we've never thought of before
        models = []
        for table_name, table_data in self.data.iteritems():
            primary = []
            for k, v in table_data['attributes'].iteritems():
                if 'primary' in v:
                    primary.append(k)
                    break

            # If not specified, a UUID is used as the PK
            if len(primary) == 0:
                table_data['attributes']['uuid'] = \
                        {'type': 'string', 'length': 36, 'primary': True, 'required': True}
                primary=['uuid']

            table_data['primary']=primary

        for table_name, table_data in self.data.iteritems():
            try:
                attrs={}
                for col_name, col_desc in table_data['attributes'].iteritems():
                    try:

                        options={}
                        args=[]

                        # Step 1: deal with object xrefs
                        if col_desc['type'] in self.data:
                            # This is a foreign key reference.  Make the column like the FK,
                            # but drop the primary from it and use the local one.
                            tgt_name = col_desc['type']
                            tgt_data = self.data[tgt_name]

                            # Confirm only one PK, we don't do multi-col refs
                            assert len(tgt_data['primary']) == 1
                            primary_col = tgt_data['primary'][0]

                            repl_col_desc = dict(tgt_data['attributes'][primary_col])

                            if 'primary' in repl_col_desc:
                                # The FK will be a primary, doesn't mean we are
                                del repl_col_desc['primary']

                            # May still be the local PK if we used to be, though
                            if col_desc.get('primary', False):
                                repl_col_desc['primary'] = True

                            # Set the SQLA col option to make clear what's going on
                            args.append(sa.ForeignKey('%s.%s' % (de_camel(tgt_name), primary_col)))

                            # The col creation code will now duplicate the FK column nicely
                            col_desc = repl_col_desc

                        # Step 2: convert our special types to ones a DB likes
                        if col_desc['type'] == 'uuid':
                            # UUIDs, from a DB perspective,  are a form of string
                            repl_col_desc=dict(col_desc)
                            repl_col_desc['type']='string'
                            repl_col_desc['length']=64
                            col_desc = repl_col_desc

                        # Step 3: with everything DB-ready, spit out the table definition
                        if col_desc.get('primary', False):
                            options['primary_key'] = True

                        required = col_desc.get('required', False)
                        options['nullable'] = not required

                        if col_desc['type']=='string':
                            attrs[col_name] = sa.Column(sa.String(col_desc['length']), *args, **options)
                        elif col_desc['type']=='integer':
                            attrs[col_name] = sa.Column(sa.Integer(), *args, **options)
                        elif col_desc['type']=='boolean':
                            attrs[col_name] = sa.Column(sa.Boolean(), *args, **options)
                        elif col_desc['type']=='enum':
                            attrs[col_name] = sa.Column(sa.Enum(*col_desc['values']), *args, **options)
                        else:
                            raise Exception('Unknown column type %s' % col_desc['type'])
                    except:
                        print('During processing of attribute ', col_name, file=sys.stderr)
                        raise

                attrs['__tablename__'] = de_camel(table_name)

                models.append(type(table_name, (base,), attrs))
            except:
                print('During processing of table ', table_name, file=sys.stderr)
                raise

        return self.Base.metadata
