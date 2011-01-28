#line 1 "inline.c"
const int len = l_;  //points array len
const int lp = lp_;  //poly array len
const int ls = ls_;  //subpoly array len
const int lpop = lt_*lp_*3/2; //population array len
const int lt = lt_;  //test array len 


Polygon* polygons = new Polygon;
Polygon* surface = new Polygon; 
polygons->points = new double[len];
polygons->poly = new int[lp];
polygons->subpoly = new int[ls];
polygons->len = lp/2;

surface->points = new double[len];
surface->subpoly = new int[ls];
surface->poly = new int[lp];
surface->len = 0;


double *population = new double[lpop];
double *test = new double[lt];


int i,j,k;

// fill the arrays with values; 
for (i=0; i<len; i++){polygons->points[i] = points_[i];}

for (i=0; i<lp; i++){polygons->poly[i] = poly_[i];}
for (i=0; i<ls; i++){polygons->subpoly[i] = subpoly_[i];}
for (i=0; i<lpop; i++){population[i] = population_[i];}

for (i=0; i<lt; i++){test[i] = test_[i];}
  
//rotate_polygon(points, subpoly, poly, 1, 10); 
test_centroid(surface, polygons, population, test, lt);

for (i=0; i<lt; i++)
{
	test_[i] = test[i];
	//printf("%d: %f\n",i,test[i]);
}


