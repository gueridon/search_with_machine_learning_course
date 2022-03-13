head -n 50000 /workspace/datasets/labeled_query_data_1000_b.txt > /workspace/datasets/query_model_1000_b.train 
tail -50000 /workspace/datasets/labeled_query_data_1000_b.txt > /workspace/datasets/query_model_1000_b.test 

~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/query_model_1000_b.train -output /workspace/datasets/query_model_1000_b -lr 0.1 -epoch 50 -wordNgrams 2
~/fastText-0.9.2/fasttext test /workspace/datasets/query_model_1000_b.bin /workspace/datasets/query_model_1000_b.test 3