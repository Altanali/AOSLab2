#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <ctime>
#include <cmath>
#include <algorithm>
#include <vector>
using namespace std;
int main(int argc, char *argv[])
{

    clock_t start, end;
    FILE* fp;
    long file_size;
    long block_size = 4096;
    char * buffer;
    size_t result;
    fp = fopen(argv[1], "r");
    if(!fp) {fputs ("File error",stderr); exit (1);}

   
      // obtain file size:
    fseek (fp , 0 , SEEK_END);
    file_size = ftell (fp);
    rewind (fp);

    long num_blocks = max(file_size/block_size, (long)(1));
    vector<int> indices(num_blocks, 0);

    // allocate memory to contain the whole file:
    buffer = (char*) malloc (sizeof(char)*block_size);
    if (buffer == NULL) {fputs ("Memory error",stderr); exit (2);}

    for(int i = 0; i < num_blocks; ++i) indices[i] = i;
    random_shuffle(indices.begin(), indices.end());
    // copy the file into the buffer:
    for(int n = 0; n < 10; ++n) {
        start = clock();
        for(int i = 0; i < num_blocks - 1; ++i) {
            fseek(fp, block_size*indices[i], SEEK_SET);
            fread (buffer, 1, block_size, fp);
        }
        end = clock();
        cout << (end - start)/(double)CLOCKS_PER_SEC << endl;
        fseek(fp, 0, SEEK_SET);
    }

    /* the whole file is now loaded in the memory buffer. */

    // terminate
    fclose (fp);
    free (buffer);
    return 0;
}