{
  curl --location --request GET 'http://0.0.0.0:5000/save_last_batches'
} || {
  echo "Error occurred!"
}