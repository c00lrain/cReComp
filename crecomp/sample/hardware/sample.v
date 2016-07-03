`timescale 1ns / 1ps
module sample(
input [32-1:0] din_32,
input [1-1:0] wr_en_32,
input [1-1:0] rd_en_32,

output [32-1:0] dout_32,
output [1-1:0] full_32,
output [1-1:0] empty_32,

inout [1-1:0] sig_out

);

reg [32-1:0] data_in;
reg [4-1:0] state_32;
reg [1-1:0] rcv_en_32;
reg [1-1:0] snd_en_32;

wire [32-1:0] data_out;
wire [32-1:0] rcv_data_32;
wire [1-1:0] data_empty_32;
wire [32-1:0] snd_data_32;
wire [1-1:0] data_full_32;

//copy this instance to top module
//sample sample(
////.clk(bus_clk)
////.rst(!user_w_write_32_open && !user_r_read_32_open),
//.din_32(user_w_write_32_data),
//.wr_en_32(user_w_write_32_wren),
//.rd_en_32(user_r_read_32_rden),
//.dout_32(user_r_read_32_data),
//.full_32(user_w_write_32_full),
//.empty_32(user_r_read_32_empty),
//.sig_out(sig_out));
parameter INIT_32 = 0,
		IDLE_32 = 1,
		READY_RCV_32 = 2,
		RCV_DATA_32_0 = 3,
		POSE_32 = 4,
		READY_SND_32 = 5,
		SND_DATA_32_0 = 6,
		CYCLE_END_32 = 7;

////fifo 32bit
fifo_32x512 input_fifo_32(
	.clk(clk),
	.srst(rst),
	.din(din_32),
	.wr_en(wr_en_32),
	.full(full_32),
	.dout(rcv_data_32),
	.rd_en(rcv_en_32),
	.empty(data_empty_32)
	);

fifo_32x512 output_fifo_32(
	.clk(clk),
	.srst(rst),
	.din(snd_data_32),
	.wr_en(snd_en_32),
	.full(data_full_32),
	.dout(dout_32),
	.rd_en(rd_en_32),
	.empty(empty_32)
	);

always @(posedge clk)begin
	if(rst)
		state_32 <= 0;
	else
		case (state_32)
			INIT_32: 		state_32 <= IDLE_32;
			IDLE_32		state_32 <=  READY_RCV_32;
			
			READY_RCV_32:			state32 <= RCV_DATA_32_0;
			RCV_DATA_32_0:			state_32 <= POSE_32;
			
			POSE_32: if(busy_sensor == 0 && finish_sensor)			state_32 <= READY_SND_32;
			READY_SND_32:		state_32 <= SND_DATA_32_0;
			SND_DATA_32_0:		state <= CYCLE_END_32;
			
			CYCLE_END_32:	state_32 <= IDLE_32;
			default: state_32 <= INIT_32;
		endcase
end

/*read block for fifo_32*/

always @(posedge clk)begin
	if(rst)begin
	
		data_in <= 0;
	end
	else if (rcv_en_32)begin
	
		data_in <= rcv_data_32[31:0];
	end
	else begin
	
		data_in <= 0;
	end
end

always @(posedge clk)begin
	if(rst_32)begin
		snd_en_32 <= 0;
		rcv_en_32 <= 0;
	end
	else case (state_32)
		READY_RCV_32: if(data_empty_32 == 0)	rcv_en_32 <= 1;
		POSE_32: rcv_en_32 <= 0;
		READY_SND_32:	if(date_full_32 == 0)	snd_en_32 <= 1;
		SND_DATA_32_0: snd_en_32 <= 0;
	endcase
end
assign snd_data_32[31:0] = data_out;
endmodule