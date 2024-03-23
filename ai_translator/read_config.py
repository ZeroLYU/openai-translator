from utils import ArgumentParser, ConfigLoader, LOG


if __name__ == "__main__":
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()
    config_loader = ConfigLoader(args.config)

    config = config_loader.load_config()
    print(config['OpenAIModel'])