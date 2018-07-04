from migen import *

from convert_data import ConvertData
from hispi_decoder import HispiDecoder

class Chain(Module):
    """ Move data from one part of the processing chain to the next"""
    def __init__(self):
        self.submodules.converter = ConvertData()
        self.submodules.decoder = HispiDecoder()

        self.in_data = self.converter.in_data
        self.out_data = self.decoder.out
        
        self.t = Signal(max=100)

        # Use converter clk_out to tell us when data is ready to be moved out
        self.clock_domains.cd_hispi = ClockDomain(reset_less=True)

        self.comb += self.cd_hispi.clk.eq(self.converter.clk_out)
        self.sync.hispi += [self.decoder.in_data.eq(self.converter.output)]

        self.sync.hispi += [self.t.eq(self.t + 1)]


def test_clock_division():
    def testbench():
        f = open("test_data/test_convert.txt")
        i = 1
        previous_data = 0

        for line in f:
            i += 1
            if i > 10:
                break

            # import pdb; pdb.set_trace()
            yield dut.in_data.eq(int(line.strip(), 2))
            yield

            # new data is moved in every second clock cycle
            print("conv out: ", format((yield dut.converter.output), 'b'))
            print("dec in: ", format((yield dut.decoder.in_data), 'b'))
            print("clock out: ", (yield dut.converter.clk_out))
            print("clock in counter: ", (yield dut.t))
            print()
            if i % 2 == 0:
                word = (yield dut.converter.output)
                assert (yield dut.decoder.in_data) == word
            else:
                pass
                # assert (yield dut.decoder.in_data) == previous_data

        assert False


    dut = Chain()
    run_simulation(dut, testbench(), clocks = {'sys': 10, 'hispi': (20, 5)})


