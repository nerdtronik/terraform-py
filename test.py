from terraform_python import Terraform, log

proc = log.start("whole process")
tf = Terraform(chdir="./tests/terraform", color=False, workspace="test")
vars = {"bucket_name": "test_bucket", "test_variable": {"test1": 1, "test2": None}}
tf.fmt()
# log.info(tf.version())
log.info(
    tf.init(
        upgrade=True,
    )
)
tf.validate()
log.info(tf.get())
# log.sep()
log.info(tf.plan(vars=vars))
# log.sep()
# tf.taint("random_string.random", vars=vars)
# tf.untaint("random_string.random")
log.info(tf.refresh(vars=vars, parallelism=30))
log.info(tf.plan(vars=vars))
log.info(tf.show(json=True))
log.info(tf.apply())
log.info(tf.output(json=True).result)
state = tf.state.pull().result
with open("./tests/terraform/terraform.tfstate","w+") as file:
    file.write(state)
log.info(tf.state.list(state_file="terraform.tfstate").__dict__)
log.info(tf.state.show())
# log.info(state)
# log.info(tf.state.push(file_content=state, force=True).__dict__)
# log.info(tf.destroy(vars=vars))

log.info(tf.state.rm("random_password.xd").result)
log.info(tf.workspace.list().__dict__)
log.info(tf.workspace.select("test", or_create=True).__dict__)
# log.info(tf.workspace.current)
log.finish(proc)
# print(state)

