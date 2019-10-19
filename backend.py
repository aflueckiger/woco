#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Project: Word Continuum: WoCo Explorer

# Backend that includes all queries to retrieve information from DB

import psycopg2


# Parameters for DB connection
connection = {
    "host": "***",
    "port": 0000,
    "user": "***",
    "dbname": "***",
    "password": "***",
}


def extract_term_relations(searchwords, language, filterwords):
    """
    Method to work with
    """

    # Set DB connection
    conn = psycopg2.connect(**connection)

    # Set DB cursor
    cur = conn.cursor()

    # Set DB scheme based on given language
    cur.execute("SET search_path TO %s, fullep", ("fullep_" + language,))

    # Execute query
    cur.execute(
        """
        WITH list AS (
        SELECT *,
            COUNT(*) OVER (PARTITION BY term_lemma) AS term_links,          -- number of links of respective search term
            COUNT(*) OVER (PARTITION BY context_lemma) AS context_links     -- number of links of respective context word
        FROM (
            SELECT term_lemma,                                              -- respective search term
            tt_lemmastr.val AS context_lemma,                               -- respective context word
            COUNT(*) AS c_relation                                          -- number of observed relations between those words
            FROM (
                SELECT tt_lemmastr.val AS term_lemma,
                typestr.val AS term_token,
                segment_id
                FROM token
                JOIN typestr ON typestr.aid = token.type_id
                JOIN tt_lemma ON tt_lemma.uid = token.token_id
                JOIN tt_lemmastr ON tt_lemmastr.aid = tt_lemma.aid
                WHERE tt_lemmastr.val IN (SELECT unnest(%s))               -- limit on searched terms
            ) AS terms
            JOIN token AS context ON terms.segment_id = context.segment_id
            JOIN typestr ON typestr.aid = context.type_id
            JOIN tt_lemma ON tt_lemma.uid = context.token_id
            JOIN tt_lemmastr ON tt_lemmastr.aid = tt_lemma.aid
            WHERE term_lemma <> tt_lemmastr.val AND tt_lemmastr.val NOT IN (SELECT unnest(%s))  -- exclude relations with itself and predefined stopwords
            GROUP BY term_lemma, context_lemma                                          -- grouping per distinct relation
        ) AS relations
        ORDER BY c_relation DESC                                                        -- order by number of occurrences of a observed relation
        ),
        indexing AS (
        SELECT *, row_number() OVER (ORDER BY links DESC) - 1 AS id                     -- indexing nodes (both lemma and context) ordered by degree of nodes (number of neighbours)
        FROM
        (
            SELECT DISTINCT term_lemma AS name, true AS is_term, term_links AS links
            FROM list
            UNION
            SELECT DISTINCT context_lemma AS name, false AS is_term, context_links AS links
            FROM list
        ) x
        ),
        nodes AS (
        SELECT jsonb_agg(jsonb_build_object('name', name, 'is_term', is_term, 'links', links)) AS obj
        FROM indexing
        ),
        links AS (
        SELECT jsonb_agg(jsonb_build_object('source', source.id, 'target', target.id, 'value', c_relation)) AS obj
        FROM list
        JOIN indexing AS source ON source.name = list.term_lemma AND source.is_term
        JOIN indexing AS target ON target.name = list.context_lemma AND NOT target.is_term
        )
        SELECT jsonb_build_object('nodes', nodes.obj, 'links', links.obj)
        FROM nodes, links
    """,
        (searchwords, filterwords),
    )

    # Retrieve results
    res = cur.fetchall()

    # Close DB connection
    cur.close()
    conn.close()

    return res


def lemma_count(words):
    """
    Unused method
    """
    # Set DB connection
    conn = psycopg2.connect(**connection)

    # Set DB cursor
    cur = conn.cursor()

    # Select German DB
    cur.execute("SET search_path TO fullep_de, fullep")

    # Execute query
    cur.execute(
        """
        SELECT tt_lemmastr.val AS lemma, count(*) AS count
        FROM token
        JOIN tt_lemma ON tt_lemma.uid = token.token_id
        JOIN tt_lemmastr ON tt_lemmastr.aid = tt_lemma.aid
        WHERE tt_lemmastr.val  IN (SELECT unnest(%s))
        GROUP BY tt_lemmastr.val
    """,
        (words,),
    )

    # Sort results into dictionary
    res = {}
    for row in cur:
        res[row[0]] = row[1]

    # Close DB connection
    cur.close()
    conn.close()

    return res


def token_count(words):
    """
    Unused method
    """
    # Set DB connection
    conn = psycopg2.connect(**connection)

    # Set DB cursor
    cur = conn.cursor()

    # Select German DB
    cur.execute("SET search_path TO fullep_de, fullep")

    # Execute query
    cur.execute(
        """
        SELECT typestr.val AS typestr, count(*) AS c
        FROM token
        JOIN typestr ON typestr.aid = token.type_id
        WHERE typestr.val IN (SELECT unnest(%s))
        GROUP BY typestr.val
    """,
        (words,),
    )

    # Sort results into dictionary
    res = {}
    for row in cur:
        res[row[0]] = row[1]

    # Close DB connection
    cur.close()
    conn.close()

    return res
