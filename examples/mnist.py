#!/usr/bin/env python

from argparse import ArgumentParser

from theano import tensor

from blocks.algorithms import GradientDescent, SteepestDescent
from blocks.bricks import MLP, Tanh, Softmax
from blocks.bricks.cost import CategoricalCrossEntropy, MisclassficationRate
from blocks.initialization import IsotropicGaussian, Constant
from blocks.datasets import DataStream
from blocks.datasets.mnist import MNIST
from blocks.datasets.schemes import SequentialScheme
from blocks.extensions import FinishAfter, Printing
from blocks.extensions.saveload import SerializeMainLoop
from blocks.extensions.monitoring import DataStreamMonitoring
from blocks.main_loop import MainLoop


def main(save_to, num_epochs):
    mlp = MLP([Tanh(), Softmax()], [784, 100, 10],
              weights_init=IsotropicGaussian(0, 0.01),
              biases_init=Constant(0))
    mlp.initialize()
    x = tensor.matrix('features')
    y = tensor.lmatrix('targets')
    probs = mlp.apply(x)
    cost = CategoricalCrossEntropy().apply(y.flatten(), probs)
    error_rate = MisclassficationRate().apply(y.flatten(), probs)

    mnist_train = MNIST("train")
    mnist_test = MNIST("test")

    main_loop = MainLoop(
        mlp,
        DataStream(mnist_train,
                   iteration_scheme=SequentialScheme(
                       mnist_train.num_examples, 50)),
        GradientDescent(cost=cost,
                        step_rule=SteepestDescent(learning_rate=0.1)),
        extensions=[FinishAfter(after_n_epochs=num_epochs),
                    DataStreamMonitoring(
                        [cost, error_rate],
                        DataStream(mnist_test,
                                   iteration_scheme=SequentialScheme(
                                       mnist_test.num_examples, 500)),
                        prefix="test"),
                    SerializeMainLoop(save_to),
                    Printing()])
    main_loop.run()

if __name__ == "__main__":
    parser = ArgumentParser("An example of training an MLP on"
                            " the MNIST dataset.")
    parser.add_argument("--num-epochs", type=int, default=2,
        help="Number of training epochs to do.")
    parser.add_argument("save_to", default="mnist.pkl", nargs="?",
        help="Destination to save the state of the training process.")
    args = parser.parse_args()
    main(args.save_to, args.num_epochs)