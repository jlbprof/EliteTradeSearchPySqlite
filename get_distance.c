/*
 * Author: Julian Brown
 * Original Date: Sept 04, 2018
 * License: MIT License, a copy of the license is in this repo
 *
 * get_distance
 *
 * This program was used primarily to test the output of calc_distance.
 * This will take to id's on the command line and find the position in
 * distances_matrix.bin and read the uint16_t and print it out.
 *
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

int max_count = 0;

char systems_fname []   = "system_master_list.csv";
char max_count_fname [] = "max_count.txt";
char matrix_fname    [] = "distance_matrix.bin";

#define MAX_BUFFER 1024

/* If this were not just used for testing, I would put these
 * routines into a module, but I do not need it really in any
 * other module.
 *
 * If I expand this set of programs that should be one of the
 * first things done.
 */

void strip_crlf (char *str)
{
    int     i = 0;

    while (str [i] != 0)
    {
        if (str [i] == '\n')
        {
            str [i] = 0;
            return;
        }
        i++;
    }

    return;
}

int find_char_or_end (
    char    *buffer,
    char    cc)
{
    int     i;
    char    myCC;

    i = 0;
    while (1)
    {
        myCC = buffer [i];
        if (myCC == cc)
            return i;

        i++;
        if (buffer [i] == 0)
            return i;
    }

    return 0; /* should never get here, keeping lint happy though */
}

char *get_token_next (
    char    *buffer)
{
    int             i;
    static char     myBuffer [MAX_BUFFER];
    char            buffer1 [MAX_BUFFER];

    i = find_char_or_end (buffer, ',');
    strcpy (myBuffer, buffer);
    myBuffer [i] = 0;

    if (buffer [i] != 0)
    {
        strcpy (buffer1, &buffer [i + 1]);
        strcpy (buffer, buffer1);
    }

    return &myBuffer [0];
}

int get_token_int (
    char    *buffer)
{
    return atoi (get_token_next (buffer));
}

double get_token_double (
    char    *buffer)
{
    return atof (get_token_next (buffer));
}

void usage (char *msg)
{
    printf ("Error: %s\n", msg);
    printf ("usage: get_distance id1 id2\n");
    exit (1);
}

int main (
    int     argc,
    char*   argv [])
{
    FILE        *file;
    char        buffer  [MAX_BUFFER];
    char        buffer1 [MAX_BUFFER];
    int         idx;
    int         id;

    int         id1;
    int         id2;

    int         idx1 = -1;
    int         idx2 = -1;
    int         pos;

    uint16_t    uDistance;

    if (argc < 3)
        usage ("not enough parameters");

    id1 = atoi (argv [1]);
    id2 = atoi (argv [2]);

    file = fopen (max_count_fname, "r");
    if (file == NULL)
    {
        printf ("Failed to open %s\n", max_count_fname);
        return 1;
    }

    if (fgets (buffer, MAX_BUFFER, file) == NULL)
    {
        fclose (file);
        printf ("Failed to read max_count.txt\n");
        return 1;
    }

    fclose (file);

    max_count = atoi (buffer);

    printf ("MAX_COUNT :%d:\n", max_count);

    /* now find the idx's of the 2 id's so we can get the position
     * calculated.
     */

    file = fopen (systems_fname, "r");
    if (file == NULL)
    {
        printf ("Failed to open %s\n", systems_fname);
        return 1;
    }

    while (fgets (buffer, MAX_BUFFER, file) != NULL)
    {
        strip_crlf (buffer);
        strcpy (buffer1, buffer);

        idx = get_token_int (buffer1);
        id  = get_token_int (buffer1);

        if (id == id1)
            idx1 = idx;

        if (id == id2)
            idx2 = idx;

        if (idx1 != -1 && idx2 != -1)
            break;
    }

    fclose (file);

    if (id1 == -1)
        usage ("id1 is invalid");

    if (id2 == -1)
        usage ("id2 is invalid");

    file = fopen (matrix_fname, "r");
    if (file == NULL)
        usage ("cannot open distance matrix file");

    pos = ((idx1 * max_count) + idx2) * sizeof (uint16_t);

    fseek (file, pos, SEEK_SET);

    fread ((void*)&uDistance, sizeof (uDistance), 1, file);
    fclose (file);

    printf ("%d\n", uDistance);

    return 0;
}

