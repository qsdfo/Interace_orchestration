import importlib
import click
import os
import torch

from DatasetManager.dataset_manager import DatasetManager
from Transformer.transformer import Transformer
from Transformer.generation.index_sampling.import_sampler import import_sampler
import Transformer.dataset_import as dataset_import
from Interface_orchestration.osc_server_live import OrchestraServerLive


@click.command()
@click.option('--in_port', type=int, default=5001)
@click.option('--out_port', type=int, default=5002)
@click.option('--ip', type=str, default="127.0.0.1")
@click.option('--config', type=str)
def main(in_port, out_port, ip, config):
    # Devices
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    gpu_ids = [int(gpu) for gpu in range(torch.cuda.device_count())]
    print(gpu_ids)

    # Load configs
    config_path = config
    config_module_name = os.path.splitext(config)[0].replace('/', '.')
    config = importlib.import_module(config_module_name).config
    model_path = os.path.dirname(config_path)

    # Get dataset
    dataset_manager = DatasetManager()
    dataset, processor_decoder, processor_encoder, processor_encodencoder = \
        dataset_import.get_dataset(dataset_manager, config['dataset'], config['num_heads'], config['per_head_dim'],
                                   config['local_position_embedding_dim'], config['block_attention'], config['nade'],
                                   config['cpc_config_name'], config['double_conditioning'],
                                   config['instrument_presence_in_encoder'], config['encoder_mask'], device)

    # Load model
    model = Transformer(dataset=dataset,
                        data_processor_encodencoder=processor_encodencoder,
                        data_processor_encoder=processor_encoder,
                        data_processor_decoder=processor_decoder,
                        num_heads=config['num_heads'],
                        per_head_dim=config['per_head_dim'],
                        position_ff_dim=config['position_ff_dim'],
                        enc_dec_conditioning=config['enc_dec_conditioning'],
                        hierarchical_encoding=config['hierarchical'],
                        block_attention=config['block_attention'],
                        nade=config['nade'],
                        conditioning=config['conditioning'],
                        double_conditioning=config['double_conditioning'],
                        num_layers=config['num_layers'],
                        dropout=config['dropout'],
                        input_dropout=config['input_dropout'],
                        input_dropout_token=config['input_dropout_token'],
                        lr=config['lr'],
                        reduction_flag=False,
                        gpu_ids=gpu_ids,
                        mixup=config['mixup'],
                        scheduled_training=config['scheduled_training'],
                        model_path=model_path
                        )

    sampler = import_sampler(config['sampler_type'])(shuffle_blocks=config['shuffle_blocks'],
                                                     maintain_t_start_order=config['maintain_t_start_order'],
                                                     shuffle_inside_blocks=config['shuffle_inside_blocks'],
                                                     shuffle_voices_inside_blocks=config[
                                                         'shuffle_voices_inside_blocks'],
                                                     parallel_sampling=config['parallel_sampling'])

    model.load(overfit_flag=True, device=device)
    model.to(device)
    model = model.eval()

    # Dir for writing generated files
    writing_dir = f'{os.getcwd()}/generation'
    if not os.path.isdir(writing_dir):
        os.makedirs(writing_dir)

    # Create server
    server = OrchestraServerLive(in_port,
                                 out_port,
                                 model=model,
                                 sampler=sampler,
                                 subdivision=config['dataset']['subdivision'],
                                 writing_dir=writing_dir,
                                 device=device)

    # server.load_piano_score('/Users/leo/Recherche/Arte_orchestration/Orchestration/Databases/arrangement/source_for_generation/b_3_4_small.mid')
    # server.orchestrate()
    print('[Running server on ports in : %d - out : %d]' % (in_port, out_port))
    server.run()


if __name__ == '__main__':
    main()
