#line 1 "inline_functions.c"
#define PI 3.14159265359
class Polygon 
{
	public :
		double *points;
		int *poly;
		int *subpoly;
		int len;
		double cx,cy,ca;
};


void rotate_subpolygon(Polygon*  polygon, int n, double a)
{
	double s = sin(a);
	double c = cos(a);
	for (int i=polygon->subpoly[n]; i<polygon->subpoly[n+1]; i+=2)
	{
		double x = polygon->points[i];
		double y = polygon->points[i+1];
		polygon->points[i] = x*c-y*s;
		polygon->points[i+1] = x*s+y*c;
	}
}

void rotate_polygon( Polygon*  polygon, int n, double a)
{
	for (int i = polygon->poly[n*2]; i<polygon->poly[n*2+1]; i+=2)
	{
		rotate_subpolygon(polygon, i, a);
	}
}

void rotate_surface( Polygon* surface, double a)
{
	for (int i=0;i<surface->len;i++)
	{
		rotate_polygon(surface,i,a);	
	}
}


void move_subpolygon( Polygon*  polygon, int n, double x, double y)
{
	for (int i=polygon->subpoly[n]; i<polygon->subpoly[n+1]; i+=2)
	{
		polygon->points[i] += x;
		polygon->points[i+1] += y;
	}	
}


void move_polygon( Polygon*  polygon, int n, double x, double y)
{
	for (int i = polygon->poly[n*2]; i<polygon->poly[n*2+1]; i+=2)
	{
		move_subpolygon(polygon, i, x, y);
	}
}


void move_surface( Polygon*  surface, double x, double y)
{
	for (int i=0;i<surface->len;i++)
	{
		move_polygon(surface,i,x,y);	
	}
}



void subpolygon_bounds(double* bounds,  Polygon*  polygon, int n)
{
	for (int i=polygon->subpoly[n]; i<polygon->subpoly[n+1]; i+=2)
	{
		if (bounds[0]>polygon->points[i])
		{bounds[0]=polygon->points[i];}
		if (bounds[2]<polygon->points[i])
		{bounds[2]=polygon->points[i];}
		if (bounds[1]>polygon->points[i+1])
		{bounds[1]=polygon->points[i+1];}
		if (bounds[3]<polygon->points[i+1])
		{bounds[3]=polygon->points[i+1];}
	}

} 


double* polygon_bounds(double* bounds, Polygon*  polygon, int n)
{
	bounds[0] =  1E+37;
	bounds[1] =  1E+37;
	bounds[2] = -1E+37;
	bounds[3] = -1E+37;
	for (int i = polygon->poly[n*2]; i<polygon->poly[n*2+1]; i+=2)
	{
		subpolygon_bounds(bounds, polygon, i);
	}
	return bounds;
} 

void surface_bounds(double* bounds, Polygon*  surface)
{
	bounds[0] =  1E+37;
	bounds[1] =  1E+37;
	bounds[2] = -1E+37;
	bounds[3] = -1E+37;
	for (int n=0; n<surface->len;n++)
	{
		for (int i = surface->poly[n*2]; i<surface->poly[n*2+1]; i+=2)
		{
			subpolygon_bounds(bounds, surface, i);
		}
	}
} 

double minf(double a, double b)
{
	return a<b?a:b;
}


double atan2(double x, double y)
{
	// returns atan for the normalized vector or (cos,sin)
	if (y==0) {return x<0?PI/2:-PI/2;}
	else {return atan(x/y);}
}




void echo_surface(Polygon* surface, std::string name="    ", bool with_points=false)
{
	std::cout<<"****************"<<std::endl<<"* "<<name<<std::endl<<"****************"<<std::endl;
	for (int k=0; k<surface->len;k++)
	{
		std::cout<<"Surface poly: "<<surface->poly[k*2]<<"-"<<surface->poly[k*2+1]<<std::endl;
		std::cout<<"Surface subpoly: ";
		for (int t =surface->poly[k*2];t<surface->poly[k*2+1]; t+=2)
		{
			printf(" %d-%d\n",surface->subpoly[t],surface->subpoly[t+1]);
		}
		std::cout<<std::endl;
	}
		printf("---------- Centroid X %f\nCentroid Y %f\nCentroid A %f\n",surface->cx,surface->cy,surface->ca);

	
}


void echo_subpolygon( Polygon*  polygon, int n)
{
	for (int i=polygon->subpoly[n]; i<polygon->subpoly[n+1]; i+=2)
	{
		printf("(%f, %f) ",polygon->points[i], polygon->points[i+1]);
	}	
}


void echo_polygon( Polygon*  polygon, int n, std::string name="    ")
{
	std::cout<<"****************"<<std::endl
		<<"* "<<name<<std::endl
		<<"* Polygon "<<n<<std::endl
		<<"****************"<<std::endl;

	for (int i = polygon->poly[n*2]; i<polygon->poly[n*2+1]; i+=2)
	{
		echo_subpolygon(polygon, i);
		std::cout<<std::endl<<"--------"<<std::endl;
	}
}


void polygon_centroid(double* centroid, Polygon* polygon, int n, bool return_mass=false)
{
	double x1,y1,x2,y2,  cx,cy,a,   sx,sy,sa,	k;
	sx = 0; sy = 0; sa = 0;
	for (int i = polygon->poly[n*2]; i<polygon->poly[n*2+1]; i+=2)
	{
		cx=0; cy=0; a = 0;
		for (int j=polygon->subpoly[i];j<polygon->subpoly[i+1]-2;j+=2)
		{
			x1 = polygon->points[j];
			y1 = polygon->points[j+1];
			x2 = polygon->points[j+2];
			y2 = polygon->points[j+3];
			k  = (x1*y2-x2*y1);
			cx += (x1+x2)*k;
			cy += (y1+y2)*k;
			a  += k;
		}
		sx += cx;
		sy += cy;
		sa += a*3;
	}
	if (sa==0)
	{centroid[0]=0; centroid[1]=0;}
	else
	{centroid[0]=sx/sa; centroid[1]=sy/sa;}
	
	if (return_mass){centroid[2] = a;}
		
}




double vertex_to_segment_vertical_dist(double x,double y,  double x1,double y1, double x2,double y2) //xy - vertex x1,y1, x2,y2 - line segment
{
	if ((x1<=x && x<=x2) || (x2<=x && x<=x1)) 
	{
		if (x1==x2) {return fabs(minf(y-y2,y-y1));}
		else {return fabs(y-y1-(y2-y1)*(x-x1)/(x2-x1));}
	}
	return -1;	
}


void drop_polygon_down(Polygon* surface, int n)
{
	//	Polygon is array of subpoly which are ranges from points array
	//	Surface is like a points array
	//	Down means min y (0,-1)  	
	double s_bounds[4];
	surface_bounds(s_bounds ,surface);
	double bounds[4];
	polygon_bounds(bounds, surface, n);
	
	// move polygon to the top of surface + 10
	move_polygon(surface, n, 0, s_bounds[3] - bounds[1] + 10);
/*
	# Now get shortest distance from surface to polygon in positive x=0 direction
	# Such distance = min(distance(vertex, edge)...)  where edge from surface and 
	# vertex from polygon and vice versa...
*/
	double dist = 1e37;
	double d;

	for (int n_s=0; n_s<surface->len;n_s++)
	{	
		for(int i=surface->poly[n_s*2];i<surface->poly[n_s*2+1];i+=2)
		{
			for (int j=surface->subpoly[i];j<surface->subpoly[i+1]-2;j+=2)
			{

				for(int i1=surface->poly[n*2];i1<surface->poly[n*2+1];i1+=2)
				{
					for (int j1=surface->subpoly[i1];j1<surface->subpoly[i1+1]-2;j1+=2)
					{
						// polygon vertex to surface
						d = vertex_to_segment_vertical_dist( surface->points[j1],surface->points[j1+1],  surface->points[j],surface->points[j+1], surface->points[j+2],surface->points[j+3]);
						if (d>=0 && dist>d){dist=d;}	
						// surface vertex to polygon
						d = vertex_to_segment_vertical_dist( surface->points[j],surface->points[j+1],  surface->points[j1],surface->points[j1+1], surface->points[j1+2],surface->points[j1+3]);
						if (d>=0 && dist>d){dist=d;}	
					}
					
				
				}
		
			}
		
		}
		
	}
	
	if (dist<1e37)
	{
		move_polygon(surface,n,0, -dist);
	}
}

void surface_append_polygon(Polygon* surface, Polygon* polygons, int n)
{
	int start_point = 0;
	int start_subpoly = 0;
	int len = surface->len;

	//echo_surface(polygons, "polygon");
	//std::cout<<std::endl<<"Appending polygon #"<<n<<std::endl;
	//std::cout<<"Appending subpolies #"<<polygons->poly[2*n]<<"-"<<polygons->poly[2*n+1]<<std::endl;

	if (len!=0)
	{
		start_subpoly = surface->poly[len*2-1];
		start_point = surface->subpoly[start_subpoly-1];
	}
	if (len==0)
	{
		surface->ca = 0;
		surface->cx = 0;
		surface->cy = 0;
	}
	int i1=0;
	int j1=0;
	surface->poly[len*2] = start_subpoly;
	surface->poly[len*2+1] = start_subpoly + (polygons->poly[2*n+1]-polygons->poly[2*n]);
	for(int i=polygons->poly[2*n]; i<polygons->poly[2*n+1]; i+=2)
	{
		surface->subpoly[start_subpoly+i1] = start_point+j1;
		surface->subpoly[start_subpoly+i1+1] = start_point+j1+ polygons->subpoly[i+1] - polygons->subpoly[i];


		i1+=2;
		for (int j=polygons->subpoly[i]; j<polygons->subpoly[i+1]; j++)
		{
			surface->points[start_point+j1] = polygons->points[j];
			j1++;
		}
	}
}


void surface_join_polygon(Polygon* surface)
{
	double c[3];
	polygon_centroid( c, surface, surface->len, true);
	if (surface->ca + c[2]!=0){
		surface->cx = (surface->cx*surface->ca+c[0]*c[2])/(surface->ca+c[2]);
		surface->cy = (surface->cy*surface->ca+c[1]*c[2])/(surface->ca+c[2]);
		surface->ca = surface->ca + c[2];
	}
	surface->len++;
	
	//echo_surface(surface, "After join");
}

void test_centroid(Polygon* surface, Polygon* polygons, double* population, double* test, int lt_)
{
	double surf_a=0;
	double c[3];
	double b[4];
	double l;
	double a1,a2;
	int n;
	int polylen = polygons->len;
	for (int test_n =0; test_n<lt_; test_n++)
	{
		if (test[test_n]<0)
		{
			surface->len=0;
			
			for (int i=0; i<polylen; i++)
			{
				n = int(population [test_n*polylen*3+i*3]);
				a1 = population [test_n*polylen*3+i*3+1]*2*PI;
				a2 = population [test_n*polylen*3+i*3+2]*2*PI;
				if (surface->len==0)
				{
			
					surface_append_polygon(surface, polygons, n);
					rotate_polygon(surface,0,a1+a2);
					surf_a = a2;
					surface_join_polygon(surface);
				}
				else
				{
					move_surface(surface, -surface->cx, -surface->cy);
	//				echo_polygon(surface, 0, "After move");				
					surface->cx = 0;
					surface->cy = 0;

	//				echo_polygon(surface, l);

					l = surface->len;
					surface_append_polygon(surface, polygons, n);
					polygon_centroid(c, surface, l);
					move_polygon(surface, l, -c[0], -c[1]);
			
					rotate_polygon(surface, l, a1+a2);
					rotate_surface(surface, a2 - surf_a);
					surf_a = a2;

					drop_polygon_down(surface, l);
					surface_join_polygon(surface);
	//				echo_polygon(surface, 0,"Surface");
	//				echo_polygon(surface, l,"Poly");	

				}	
			}		
	
			rotate_surface(surface, -surf_a);
			surface_bounds(b,surface);
//			printf("Test %d: %10.10f\n",test_n,(b[2]-b[0])*(b[3]-b[1]));
//			printf("Bonds: %f %f %f %f\n", b[0], b[1], b[2], b[3]);
		
			test[test_n]	= (b[2]-b[0])*(b[3]-b[1]);
		}
	}	
}
