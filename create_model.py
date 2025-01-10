from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.sql.functions import col
from pyspark.ml.evaluation import RegressionEvaluator
import os
import shutil



class Model_creator():
    def __init__(self):
        self.spark_session = SparkSession.builder.appName('MyRecommenadationSystemApp')\
            .config("spark.driver.memory", "8g") \
            .config("spark.executor.memory", "8g") \
            .config("spark.driver.extraJavaOptions", "-Xss16m").getOrCreate()
        self.moviesdf = self.spark_session.read.csv('data/movies.csv',header=True,inferSchema=True)
        self.ratingsdf = self.spark_session.read.csv('data/ratings.csv',header=True,inferSchema=True)

    def split_data(self):
        (self.training_data,self.test_data) = self.ratingsdf.randomSplit([0.9,0.1])
    

    def set_up_model(self):
        als = ALS(userCol='userId', itemCol='movieId', ratingCol='rating',coldStartStrategy='drop',rank= 30,maxIter=300,regParam=.15,)
        self.model = als.fit(self.training_data)

    def make_prediction(self):
        self.prediction = self.model.transform(self.test_data)
        self.prediction.show()
        evaluator = RegressionEvaluator(metricName='rmse', predictionCol='prediction',labelCol='rating')
        rmse = evaluator.evaluate(self.prediction)
        print(rmse)

    def create_recommendations_df(self):
        self.recommendations = self.model.recommendForAllUsers(5)
        self.recommendations.registerTempTable("ALS_recs_temp")
        clean_recs = self.spark_session.sql("SELECT userId,                                movieIds_and_ratings.movieId AS movieId,                                movieIds_and_ratings.rating AS prediction                       FROM ALS_recs_temp                      LATERAL VIEW explode(recommendations) exploded_table                       AS movieIds_and_ratings")
        a = clean_recs.join(self.moviesdf,["movieId"],'left')
        self.recommendations_df = a.select(['userId','title','genres','prediction']).sort("userId", "prediction", ascending=[True, False])
        
    def save_recomendation_to_csv(self):
        self.recommendations_df.coalesce(1).write.csv("data/temp_recommendations", header=True, mode="overwrite")
        output_dir = 'data/temp_recommendations'
        final_file = 'data/recommendations.csv'
        for file in os.listdir(output_dir):
            if file.endswith(".csv"):
                shutil.move(os.path.join(output_dir, file), final_file)
        shutil.rmtree(output_dir)




