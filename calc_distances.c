/*
 * Author: Julian Brown
 * Original Date: Sept 04, 2018
 * License: MIT License, a copy of the license is in this repo
 *
 * calc_distances
 *
 * This program helps deal with a pretty intense calculational
 * problem.   There are about 21,000 star systems in the
 * Elite Dangerous Game Galaxy.   We need to know the
 * distance between each of the star systems in light years.
 *
 * This becomes too computationally intense to run the calculations
 * on the fly, so I have created a 2D array of the distances between
 * the different systems.
 *
 * The distances are stored using uint16_t (2 bytes) so the file does
 * not get larger than about 1gb.   If I stored it in a normal table
 * in a DB with one index that array could get to be over 32gb and
 * be untenable when populating the data.
 *
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <unistd.h>

/* each star system is represented with these values */

struct system_s
{
    int     idx;   /* the index into the array */
    int     id;    /* id in the db, this number can be in the millions */
    double  x;     /* coordinate of the star system for the distance formula */
    double  y;
    double  z;
};

typedef struct system_s system_t;

system_t* systems = NULL;

/* this is the number of star systems and the width of the 2D array */
int max_count = 0;

char systems_fname []   = "system_master_list.csv";
char max_count_fname [] = "max_count.txt";
char matrix_fname    [] = "distance_matrix.bin";

#define MAX_BUFFER 1024

/* strip off the line feed */

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

/* look for this cc or the end of the line,
 * note there are other routines that are in the
 * standard c library, but they are not really built
 * for this exact purpose, so I wrote one myself
 */

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

/* the file is a CSV (simple no character escapes),
 * so find the next comma or the end of the file and
 * return that as a string, while advancing the
 * position in the buffer.  So we can get the next one later.
 */

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

/* get the next token as an integer */
int get_token_int (
    char    *buffer)
{
    return atoi (get_token_next (buffer));
}

/* get the next token as a double */
double get_token_double (
    char    *buffer)
{
    return atof (get_token_next (buffer));
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
    double      x;
    double      y;
    double      z;

    double      distance;
    uint16_t    uDistance;

    int         i;
    int         j;

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

    /* the max_count is conveniently provided for me by updatedb.py */
    max_count = atoi (buffer);

    printf ("MAX_COUNT :%d:\n", max_count);

    /* allocate the data, I prefer calloc as everything is zero */
    systems = (system_t*)calloc (max_count, sizeof (system_t));

    /* now open the file and fill up systems */
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

        /* the format should be
         * idx,id,x,y,z
         */

        idx = get_token_int (buffer1);
        id  = get_token_int (buffer1);
        x   = get_token_double (buffer1);
        y   = get_token_double (buffer1);
        z   = get_token_double (buffer1);

        systems [idx].idx = idx;
        systems [idx].id  = id;
        systems [idx].x   = x;
        systems [idx].y   = y;
        systems [idx].z   = z;
    }

    fclose (file);

    /* this is an O(n*n) problem and although it could be halfed,
     * by only calculating a pair once and filling in the opposite
     * location, the difference is not worth the effort.
     */

    unlink (matrix_fname);
    file = fopen (matrix_fname, "w");
    if (file == NULL)
    {
        printf ("Cannot open :%s:\n", matrix_fname);
        return 1;
    }

    for (i = 0; i < max_count; ++i)
    {
        for (j = 0; j < max_count; ++j)
        {
            if (i == j)
                uDistance = 0;
            else
            {
                /* distance formula */

                double dx;
                double dy;
                double dz;

                dx = systems [i].x - systems [j].x;
                dy = systems [i].y - systems [j].y;
                dz = systems [i].z - systems [j].z;

                distance = sqrt (dx * dx + dy * dy + dz * dz);
                if (distance < 0.0)
                    uDistance = 0;
                else
                {
                    distance += 0.5;  /* to help with rounding */
                    if (distance > 65535.0)
                        uDistance = 65535;
                    else
                        uDistance = (uint16_t)distance;
                }
            }

            fwrite ((const void*)&uDistance, sizeof (uDistance), 1, file);
        }
    }

    fclose (file);

    return 0;
}

