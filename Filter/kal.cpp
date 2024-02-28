#include <opencv2/opencv.hpp>
 
/*
"**" after "//" means the values are relative to Kalman regression speed.
*/
 
using namespace std;
using namespace cv;
 
namespace Kalman_example
{
class KalmanFilter
{
public:
	KalmanFilter(int x, int y):
		KF_(4, 2)
		/*
		KalmanFilter( int dynamParams, int measureParams, int controlParams = 0, int type = CV_32F )
		"dynamParams = 4": 4*1 vector of state (x, y, delta x, delta y)
		"measureParams = 2": 2*1 vector of measurement (x, y)
		*/
        {
            measurement_ = Mat::zeros(2, 1, CV_32F);// (x, y)
            KF_.transitionMatrix = (Mat_<float>(4, 4) << 1, 0, 1, 0,//**Latter 1: Larger, faster regression
                                                         0, 1, 0, 1,//**Latter 1: Larger, faster regression
                                                         0, 0, 1, 0,
                                                         0, 0, 0, 1);
            setIdentity(KF_.measurementMatrix, Scalar::all(1));
            setIdentity(KF_.processNoiseCov, Scalar::all(1e-3));//**3: Larger, slower regression
            setIdentity(KF_.measurementNoiseCov, Scalar::all(1e-1));//1: Larger, quicker regression
            setIdentity(KF_.errorCovPost, Scalar::all(1));
 
            KF_.statePost = (Mat_<float>(4, 1) << x, y, 0, 0);//Ensure beginner is default value
        }
 
	Point2f run(float x, float y)
	{
		Mat prediction = KF_.predict();
		Point2f predict_pt = Point2f(prediction.at<float>(0),prediction.at<float>(1));
 
		measurement_.at<float>(0, 0) = x;
		measurement_.at<float>(1, 0) = y;
 
		KF_.correct(measurement_);
 
		return predict_pt;
	}
private:
	Mat measurement_;
	cv::KalmanFilter KF_;//Differ from Kalman_example::KalmanFilter
};
 
}
 
 
int main()
{
	float size_x = 1280;//cols of side
	float size_y = 480;//rows of side
	float x = 20;//CV_32F: float
	float y = 240;//CV_32F: float
	int color = 0;//gradually varied color
 
	Mat image(size_y, size_x, CV_8UC3);
 
	Kalman_example::KalmanFilter kf(x, y);//Differ from cv::KalmanFilter
 
	Point2f currentPoint(x,y);
	Point2f kalmanPoint(x,y);
 
	while(1)
	{
		//image = Scalar(0,0,0);//Clear points before
		currentPoint = Point2f(x,y);
		kalmanPoint = kf.run(x,y);
 
		circle(image,kalmanPoint,3,Scalar(0,255,0 + color),2);//predicted point with green
		circle(image,currentPoint,3,Scalar(255,0,0 + color),2);//current position with red
 
		imshow("KalmanPoint", image);
		cout << "Current: " << currentPoint << " Kalman: " << kalmanPoint << endl;
 
		x+=105;
		//y+=10;
		color+=20;
		waitKey(1000);
 
		if(color>=255)
		{
			color = 255;
		}
		if((x>=size_x) || (y>=size_y) || (x<=0) || (y<=0))
		{
			imwrite("KalmanPoint.jpg", image);
			break;
		}
	}
 
	return 0;
}
 