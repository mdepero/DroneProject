#include <boost/python.hpp>

#if defined(_MSC_VER) && (_MSC_VER >= 1800)
// eliminating duplicated round() declaration
#define HAVE_ROUND 1
#endif

#include "DroneUtils.h"
using namespace cv;
using namespace std;


std::vector<KeyPoint> findPaper (Mat frame, double avgBright) {

  //This stuff is setting up the images by
  //    Saving the HSV version of the image
  //    Saving the Gray version of the image
  //    Blurring the grayed image
  Mat colors[3];
  Mat colored;
  Mat copy;
  frame.copyTo(colored);
  cvtColor(colored,colored,CV_BGR2HSV);
  split(frame,colors);
  copy = frame;
  cvtColor(frame,frame,CV_BGR2GRAY);
  GaussianBlur(frame,frame,Size(3,3),0);
  ///////////////////////////////////////////
   

  //This is an iterative deepening kind of thing, starting keypoint detection 
  //with a large param to find points faster, then going smaller to find more
  //points
  for(int parameter = 10; parameter > 0; parameter--) {
   
    double offset = 1; //An offset to look at neighbors of key points later

    std:vector<KeyPoint> points;
    std::vector<KeyPoint> allPoints;

    //KeyPoint detection
    //////////////////////////////////////////////////////////////////////
    FAST(frame,allPoints,parameter);
    //////////////////////////////////////////////////////////////////////

    do {      //holy crap a do while loop
      points = std::vector<KeyPoint>(allPoints);
      std::vector<int> keep(points.size()); //Create a vector of ints that will store if they are good points or not

      for (std::vector<KeyPoint>::iterator it = points.begin(); it != points.end(); it++) { //Check all the points
	KeyPoint pt = *it;
	Vec3b at = colored.at<Vec3b>(pt.pt); //Get HSV value of the point
	int numRed = 0;
	int numWhite = 0;

	//This section defines the neighbors we are looking at. They are the change in row and change in column.
	//Im a math guy so I call them deltas
	 double dr[8] = { 0, -1,-1, -1, 0,  1, 1, 1};
	 double dc[8] = { 1, 1,  0, -1,-1,-1, 0, 1};
	 std::vector<int> deltaRow (dr, dr+sizeof(dr)/sizeof(int));
	 std::vector<int> deltaCol (dc, dc+sizeof(dc)/sizeof(int));
  	  
	 for(unsigned int i = 0; i < deltaRow.size(); i++) {
	   KeyPoint delta = pt; //Start with the keypoint we are looking at
	   int rowAdd = offset; //Save the offset
	   int colAdd = offset;
	  
	   delta.pt.x = pt.pt.x + (int) (deltaRow[i] * rowAdd); //Offset the coordinates
	   delta.pt.y = pt.pt.y + (int) (deltaCol[i] * colAdd);

	   //Makes sure the neighbor coordinate makes sense to check
	   if(delta.pt.x < 0 || delta.pt.y < 0 || delta.pt.x >= frame.cols || delta.pt.y >= frame.rows) { 
	     continue;
	   }
	   
	   int colorCode = 0; //This variable is the "code" of the color, either 0 if neigher red or white, 1 if red, 2 if white
	   Vec3b neighbor = colored.at<Vec3b>(delta.pt);

	   int count = 0; //This counts the number of values of 255 in the HSV colors. Each value is probably not exactly 255, unless I had previously messed with it, which I do below
	   for(int i = 0; i < 3; i++) {
	     if((int)neighbor[i] == 255){count++;} 
	   }
	   
	   if(count >= 2){ //If it has 2 or more 255s, I changed it before. This seems to make the algorithm faster, but I'm not sure whyy
	     continue;
	   }
	   
	   if((neighbor[0] > LOW_RED || neighbor[0] < HIGH_RED) && neighbor[1] > 73 && neighbor[2] > 50) { //Carefully defined values for red
	     numRed++;
	     colorCode = 1;
	   } else if( neighbor[2] > avgBright) { //I figure, white is bright in HSV, so if the value of a pixel is greater than the average, it is probably white
	     numWhite++;
	     colorCode = 2;
	   }
	  
	   //Debugging code, this doesn't do anything important.
	   /////////////////////////////////////////////////////////
	   if(colorCode == 0) { 
	    colored.at<Vec3b>(delta.pt)[0]= 255;
	    colored.at<Vec3b>(delta.pt)[1] = 255;
	    colored.at<Vec3b>(delta.pt)[2] = 255;
	  } else if (colorCode == 1) {
	    colored.at<Vec3b>(delta.pt)[0]= 100;
	    colored.at<Vec3b>(delta.pt)[1] = 255;
	    colored.at<Vec3b>(delta.pt)[2] = 255;
	  } else if (colorCode == 2) {
	    colored.at<Vec3b>(delta.pt)[0]= 10;
	    colored.at<Vec3b>(delta.pt)[1] = 255;
	    colored.at<Vec3b>(delta.pt)[2] = 255;
	  }
	   ////////////////////////////////////////////////////////

	}  

	 //If the keypoint we are looking at does not have 5 red neighbors and 3 white, we don't want it
	if(numRed != 5 ||( numWhite != 3 )) {
	  keep[it - points.begin()] = -1;
	}
      }
      
      //Deletes all of the points that do not satisfy the criteria
      int size = points.size();
      int trueIndex = 0;
      int loopIndex = 0;
      
      while(trueIndex < size) {
	if(keep[trueIndex] == -1) {
	  points.erase(points.begin()+loopIndex);
	  
	  trueIndex++;
	} else {
	  loopIndex++;
	  trueIndex++;
	}
      }
      offset++;
    } while(points.size() != 4 && offset < 20); //Stops when the offset is large enough, to go back and try FAST again

    if(points.size()%4 == 0){return points;}
    else {
      return std::vector<KeyPoint>();} //If the points couldn't form a box, return empty vector, else return the points
  } 
}



//Python version of display Image method
void displayImage(char* img, int width, int height) {
  cv::Mat image(cv::Size(width,height),CV_8UC3,img,cv::Mat::AUTO_STEP);
  for(;;) {
    cv::imshow("",image);
    char c = cv::waitKey(1);
    if(c == 27) {
      break;
    }
  }
}

//Debugging method. Use this to display an image, which will be displayed until you hit ESC (at least on Linux/Pi) 
//and then the code will keep going
void displayImageInner(Mat image) {
  for(;;) {
    cv::imshow("",image);
    char c = cv::waitKey(1);
    if(c == 27) {
      break;
    }
  }
}

//This little method gets the width of the piece of paper in pixels.

//It works by finding the distances between the first point and all the other points.
//The width is going to be the smallest out of the width,height, and diagonal, or else the paper would be rectangular
double getWidth(std::vector<KeyPoint> paper) {
  assert(paper.size() % 4 == 0);
   double dist1 = std::sqrt(std::pow(paper[0].pt.x - paper[1].pt.x,2) + std::pow(paper[0].pt.y - paper[1].pt.y,2));
  double dist2 = std::sqrt(std::pow(paper[0].pt.x - paper[2].pt.x,2) + std::pow(paper[0].pt.y - paper[2].pt.y,2));
  double dist3 = std::sqrt(std::pow(paper[0].pt.x - paper[3].pt.x,2) + std::pow(paper[0].pt.y - paper[3].pt.y,2));
  double width = std::min(dist1, std::min(dist2,dist3));
  return width;


}

//Uses the fomulas Dr. Leonard gave us to determine a distance estimation
double calculateDistance(double width, double inchWidth) {
  double distance = 0;
  distance = FOCAL_LENGTH;
  distance = distance * inchWidth;
  distance = distance / width;
  return distance;


}

//Splits an image into HSV mats, nice little helper function
void hsvSplit (Mat const img, std::vector<Mat>& vects) {
  Mat hsv[3];
  Mat hsvVersion;
  cvtColor(img,hsvVersion,CV_BGR2HSV);
  split(img,hsv);
  vects.push_back(hsv[0]);
  vects.push_back(hsv[1]);
  vects.push_back(hsv[2]);
}

//Function that is called by Python to get the distance 
//to a sheet of paper. 

//A couple notes here:
/*

The char* parameter is the actual data of the Numpy Array that is given. 
The width and height are pretty self explanitory, but I'll describe it in
more detail in the ImageProcessing.py file
 */
double getPaperDist(char * img, int width, int height) {
   cv::Mat image(cv::Size(width,height),CV_8UC3,img,cv::Mat::AUTO_STEP);
   std::vector<Mat> hsv;
   hsvSplit(image,hsv);
   double avgBright = getAverageBright(hsv);
   std::vector<KeyPoint> paper = findPaper(image,avgBright);
   double widthInPix = getWidth(paper);
   double distance = calculateDistance(widthInPix,PAPER_WIDTH);
   return distance;


}

//Returns the average brightness of an image, assuming that
//the image is divided into a vector of Mats, where each
//spot of the vector representing H S or V
double getAverageBright(std::vector<cv::Mat> const img) {
  Scalar averageBright (0);
  Scalar stdDevBright (0);
  meanStdDev(img[2],averageBright,stdDevBright);
  return averageBright[0];
}



//This part is what Python can see
//when the module is imported.
BOOST_PYTHON_MODULE(DroneUtils) {
  using namespace boost::python;
  def("displayImage",displayImage);
  def("getPaperDist",getPaperDist);
}