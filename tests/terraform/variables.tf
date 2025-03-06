variable "bucket_name" {
  type = string
}

variable "test_variable" {
  type = object({
    test1 = number
    test2 = any
  })
}
