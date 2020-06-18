// Gmsh project created on Wed Jun 17 21:44:34 2020
SetFactory("OpenCASCADE");

// exterior radius
Rext = 0.1; 
// interior radius
Rint = 0.04;
// thickness
h = .005;

Circle(1) = {-0, -0, -0, Rext, 0, 2*Pi};
Circle(2) = {0, -0.0, 0, Rint, 0, 2*Pi};

Line Loop(1) = {1};
Plane Surface(1) = {1};

Line Loop(2) = {2};
Plane Surface(2) = {2};

BooleanDifference{ Surface{1}; Delete;}{ Surface{2}; Delete;}

Extrude {0, 0, h} {Surface{1};}

Field[1] = Box;
Field[1].VIn = Rext/20;
Field[1].VOut = Rext;
Field[1].XMax = Rext;
Field[1].XMin = -Rext;
Field[1].YMax = Rext;
Field[1].YMin = -Rext;
Field[1].ZMax = h;
Field[1].ZMin = 0;
Background Field = 1;
