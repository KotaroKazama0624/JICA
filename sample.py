# coding utf-8
import pprint
import HTTPWebApp as jica

email    = 'testaccount@gmail.com'
password = 'testAccountPassword'

post_data_app = jica.HTTPWebApp(email, password)

place_id   = '2o6sB6opdUT23pPaK7A6'
student_id = '27009'
body_T     = '36.9'

pprint.pprint(post_data_app.postBodyTemperature(place_id, student_id, body_T))
