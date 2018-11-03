# How to represent a network topology

```
name_of_edge_1: x1,y1
name_of_edge_2: x2,y2
name_of_edge_3: x3,y3
<empty line>
name_of_edgeA:name_of_edgeB <number_of_lanes_in_that_direction>:<number_of_lanes_in_the_other_direction>
name_of_edgeC:name_of_edgeD <number_of_lanes_in_that_direction>:<number_of_lanes_in_the_other_direction>
```

* For simplicity, let's only use positive integer coordinates (1st quadrant).
* <name_of_edgeX> should follow the constraints of programming languages variable names (letter+underscore+number): the purpose is to use the variable names to state the edges formed (2nd part of the file).
* A pair of vertices is unique when declaring the topology in the 2nd part. 

### Example:

```
v1: 0,0
vertex2: 0,20
super_vertex: 10,20
v3: 10,0

v1:v3 1:0 // <-- one way
super_vertex:v3 2:1
super_vertex:vertex2 1:1
v1:vertex2 1:1
```
