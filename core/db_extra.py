from psycopg import sql



class DbExtra:

    def __init__(self, db, schema=None):
        self.cursor = db.cursor()
        self.schema = schema



    

    def fetchOne(self, query, params=None, **kwargs):
        """Return single value from database."""
        cursor = self.cursor
        cursor.execute(query, params, **kwargs)
        res = cursor.fetchone()

        return res[0] if res is not None else None



    def fetchColumn(self, query, params=None, **kwargs):
        cursor = self.cursor
        cursor.execute(query, params, **kwargs)
        rows = cursor.fetchall()
        result = [row[0] for row in rows]

        return result



    def fetchColumnDict(self, query, params=None, **kwargs):
        cursor = self.cursor
        cursor.execute(query, params, **kwargs)
        rows = cursor.fetchall()
        result = {row[0]: row[1] for row in rows}

        return result




    def fetchRows(self, query, params=None, **kwargs):
        cursor = self.cursor
        cursor.execute(query, params, **kwargs)
        rows = cursor.fetchall()

        return rows



    def fetchRowsDict(self, query, params=None, **kwargs):
        cursor = self.cursor
        cursor.execute(query, params, **kwargs)
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = [dict(zip(cols, row)) for row in rows]

        return result




    def fetchRowsDictIndexed(self, query, params=None, **kwargs):
        cursor = self.cursor
        cursor.execute(query, params, **kwargs)
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = {row[0]: dict(zip(cols[1:], row[1:])) for row in rows}

        return result




    def insert(self, table, columns, values, uniqueIndexColumns=None, ignoreConflicts=False, schema=None):
        """Single row insert into database."""
        query = self._prepareInsertQuery(table, columns, uniqueIndexColumns, ignoreConflicts, schema)

        self.cursor.execute(query, values)
        return self.cursor


   

    def batchInsert(self, table, columns, values, uniqueIndexColumns=None, ignoreConflicts=False, schema=None):
        """Batch insert records into database."""
        query = self._prepareInsertQuery(table, columns, uniqueIndexColumns, ignoreConflicts, schema)

        self.cursor.executemany(query, values)
        return self.cursor

  

    def _prepareInsertQuery(self, table, columns, uniqueIndexColumns=None, ignoreConflicts=None, schema=None):
        if schema is None:
            schema = self.schema

        placeholders = sql.SQL(',').join(sql.Placeholder() * len(columns))
        columnsSql = sql.SQL(',').join([sql.Identifier(col) for col in columns])
        uniqueIndexColumnsSql = None
        onConflictUpdatesSql = None

        query = "insert into {schema}.{tableName} ({columns}) values ({placeholders}) "

        if uniqueIndexColumns:
            query += "on conflict ({uniqueIndexColumns}) do "
            uniqueIndexColumnsSql = sql.SQL(',').join([sql.Identifier(col) for col in uniqueIndexColumns])
            if ignoreConflicts:
                query += "nothing"
            else:
                query += "update set {onConflictUpdates}"
                onConflictUpdatesSql = sql.SQL(',').join([
                    sql.Identifier(col) + sql.SQL(' = excluded.') + sql.Identifier(col)
                    for col in columns if col not in uniqueIndexColumns
                ])

        query = sql.SQL(query).format(
            schema=sql.Identifier(schema), tableName=sql.Identifier(table),
            placeholders=placeholders, onConflictUpdates=onConflictUpdatesSql,
            columns=columnsSql, uniqueIndexColumns=uniqueIndexColumnsSql,
        )


        return query