user_interactions = LOAD '/user/hadoop/data/user_interactions' USING PigStorage(',') AS (user_id:int, action:chararray, timestamp:long);
filtered_interactions = FILTER user_interactions BY action == 'click';
grouped_by_user = GROUP filtered_interactions BY user_id;
user_interaction_count = FOREACH grouped_by_user GENERATE group AS user_id, COUNT(filtered_interactions) AS click_count;
STORE user_interaction_count INTO '/user/hadoop/output/user_interaction_count' USING PigStorage(',');