/*********************************************/
/* Set Cover C++ v1.2                        */
/* Simulated Annealing                       */
/* Mark Mammel 2/25/14                       */
/*********************************************/
/*********************************************/
/* compile in Linux with:                    */
/*   g++ setCoversa.cpp -O3 -o setCoversa    */
/* or in Windows Microsoft Visual C++        */
/*   uncomment the first include line        */
/*********************************************/

//#include "stdafx.h" //ONLY for Microsoft Visual Studio
#include <iostream> 
#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

char fname[11]="tmp.data\0";
//char fname[14]="sc_25_0\0";
//char fout[18]="out.txt\0";
const int MAXM=1024; //maximum rows
const int MAXN=16384; //maximum columns
int N; //number of columns to choose
int M; //number of rows to cover
int pen, pencost; //number of missing rows, cost for missing a row

class HGraph
{
public:
	int cost[MAXN]; //column cost
	bool colsel[MAXN]; //column selected
	bool exclude[MAXN]; //redundant columns
	int rowfreq[MAXM]; //count of row hits
	char *t; //matrix
	bool soln[MAXN]; //best solution
	int minScr; //best score
	int numon; //number of columns selected
	int xcount; //number of excluded columns

HGraph()
{ 	/* constructor */
	t = new char[N*M];
	memset(t,0,N*M);
	minScr=1000000000;
	for (int j=0; j<N; j++)
		exclude[j]=false;
	numon=0;
}

~HGraph()
{
	delete[] t;
}

void checkCols()
{ //finds columns which are covered by a lower or equal cost column
	int i,j1,j2;
	bool ok;
	xcount=0;

	for (j1=0; j1<N; j1++)
	{ //check each column
	for (j2=0; j2<N; j2++)
	if (j1!=j2 && !exclude[j2])
	{ //vs each column
		ok=true; //is each row covered
		for (i=0; i<M; i++)
		{ 
			if (t[i*N+j1]>t[i*N+j2])
			{
				ok=false;
				break;
			}
		}
		if (ok && cost[j2]<=cost[j1])
		{
			//printf("%d in %d\n",j1,j2);
			exclude[j1]=true;
			xcount++;
			j2=N; //break
		}
	}
	}
	fprintf(stderr,"%d columns excluded\n",xcount);

}

int Score()
{ //finds total cost plus penalties of solution
	int i,j;
	int scr;

	pen=0;
	scr=0;
	for (i=0; i<M; i++)
		rowfreq[i]=0;
	for (j=0; j<N; j++)
		if (colsel[j])
		{
			for (i=0; i<M; i++)
				rowfreq[i] +=t[i*N+j];
			scr+=cost[j];
		}
		for (i=0; i<M; i++)
			if (rowfreq[i]==0)
				pen++;
	scr+=pen*pencost;

	return scr;
}

void randStart2()
{ //select enough random columns (steered by cost) to cover all rows
	int i,j,k;
	int mc,mj,rc;

	numon=0;
	for (i=0; i<M; i++)
		rowfreq[i]=0;
	for (j=0; j<N; j++)
		colsel[j]=false;
	for (i=0; i<M; i++)
	if (rowfreq[i]==0)
	{
		mc=1000000000;
		mj=0;
		for (j=0; j<N; j++)
		if (!exclude[j])
		{
			if (t[i*N+j]==1)
			{
				rc=cost[j]+rand()%100;
				if (rc<mc)
				{
					mc=rc;
					mj=j;
				}
			}
		}
		for (k=0; k<M; k++)
			rowfreq[k]+=t[k*N+mj];
		colsel[mj]=true;
		numon++;
	}

}

int testToggle(int c1)
{ //determine score change by toggling selection of column c1
	int i;
	int scr=0;

	if (colsel[c1])
	{
		for (i=0; i<M; i++)
		{
			if (rowfreq[i]==1 && t[i*N+c1]==1)
				scr+=pencost;
		}
		scr-=cost[c1];
	}
	else
	{
		for (i=0; i<M; i++)
		{
			if (rowfreq[i]==0 && t[i*N+c1]==1)
				scr-=pencost;
		}
		scr+=cost[c1];
	}

	return scr;

}

void doToggle(int c1)
{ // toggle selection status of column c1
	int i;

	if (colsel[c1])
	{
		for (i=0; i<M; i++)
			rowfreq[i] -=t[i*N+c1];
		colsel[c1]=false;
		numon--;
	}
	else
	{
		for (i=0; i<M; i++)
			rowfreq[i] +=t[i*N+c1];
		colsel[c1]=true;
		numon++;
	}

}

int testSwap(int c1, int c2)
{ //determine score change by c1 off c2 on
	int i;
	int scr=0;

	for (i=0; i<M; i++)
	{
		if (rowfreq[i]==1 && t[i*N+c1]==1 && t[i*N+c2]==0)
			scr+=pencost;
		if (rowfreq[i]==0 && t[i*N+c1]==0 && t[i*N+c2]==1)
			scr-=pencost;
	}
	scr+=cost[c2]-cost[c1];

	return scr;

}

void doSwap(int c1, int c2)
{ // c1 off c2 on
	int i;

	for (i=0; i<M; i++)
		rowfreq[i] += t[i*N+c2]-t[i*N+c1];
	colsel[c1]=false;
	colsel[c2]=true;

}

void savePath()
{ /* save current solution as best */
	int j;
	for (j=0; j<N; j++)
		soln[j]=colsel[j];

}

}; //class

void SimAnn(HGraph* hg)
{
	const double fR = 0.995;
	double fMax = (double)pencost; //starting temperature
	const double fMin = 0.1;
	const int MAXREPS=20000;
	
	double fT,fD;
	int pscr,scr;
	int c1,c2,nP, count, r;

	pscr=hg->Score();
	fT = fMax; // set start temperature

	do { //each temp
		count=0;
		do { //each rep
			//change
			r=rand()%10; //either try toggle or try swap
			if (r<6 || hg->numon==0 || hg->numon==N-hg->xcount)
			{
				do c1=rand()%N;
				while (hg->exclude[c1]);
				scr=hg->testToggle(c1);
				r=0;
			}
			else
			{
				do c1=rand()%N;
				while (!hg->colsel[c1]);
				do c2=rand()%N;
				while (hg->colsel[c2] || hg->exclude[c2]);
				scr=hg->testSwap(c1,c2);
			}
			fD=(double)scr;
			scr+=pscr;
			nP = (int)(10000.0 / (1.0 + exp(fD/fT)));

			if (scr < pscr || rand()%10000 < nP)
			{ //keep new
				if (r<6)
					hg->doToggle(c1);
				else
					hg->doSwap(c1,c2);

				pscr=scr;
				if (scr<hg->minScr)
				{
					hg->minScr=scr;
					hg->savePath();
					//fprintf(stderr,"%d\n",hg->minScr);
					//fflush(stdout);
				}
			}

		} while (++count<MAXREPS);
		fT = fR*fT; //decrease temperature
		//fprintf(stderr,"%f\n",fT); 
	} while ( fT > fMin );

}

int main()
{
	HGraph* hg;
	FILE *fp;
	int j, x, maxcost; 
	unsigned int seed;
	int rdfl;
	char ch;
	bool onon;

	seed = (unsigned)time( NULL );
	//seed = 1106337142;
	srand( seed );
	maxcost=0;
	if ((fp = fopen(fname, "r"))==NULL) 
	{
		printf("Can't open input\n");
		exit(1);
	}
	fscanf(fp,"%d %d\n",&M,&N);
	hg= new HGraph(); //must read in N and M first before construct
	for (j=0; j<N; j++)
	{
		fscanf(fp,"%d",&x);
		hg->cost[j]=x;
		if (x>maxcost)
			maxcost=x;
		x=0;
		onon=false; //valid number read
		do
		{
			rdfl=fread(&ch,sizeof(char),1,fp);
			if (ch>='0' && ch<='9' && rdfl)
			{
				x=x*10+ch-48;
				onon=true;
			}
			else if (onon)
			{
				hg->t[x*N+j]=1;
				x=0;
				onon=false;
			}
		} while (rdfl && ch!=10); //unwisely using specific ascii codes for end of line
	}
	fclose(fp);

	pencost=maxcost*4;
	hg->checkCols();
	hg->randStart2();
	SimAnn(hg);

	printf("%d 0\n", hg->minScr);
	for (j=0; j<N; j++)
	{
		if (hg->soln[j])
			printf ("1 ");
		else
			printf ("0 ");
	}
	printf("\n");

	fflush(stdout);
/*
	if ((fp = fopen(fout, "wb"))==NULL) 
	{
	  printf("Can't open out\n");
	  return 1;
	}
	fprintf(fp,"%d\n", hg->minScr);
	for (j=0; j<N; j++)
	{
		if (hg->soln[j])
			fprintf (fp,"1 ");
		else
			fprintf (fp,"0 ");
	}
	fprintf(fp,"\n");
	fclose(fp);
*/
	delete hg;

	return 0;
}
