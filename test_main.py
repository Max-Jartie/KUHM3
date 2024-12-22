import unittest
from main import parse_config


class TestParseConfig(unittest.TestCase):
    
    def test_string_values(self):
        config_text = """
        app_name := 'MyApp';
        version := '1.0.3';
        """
        config = parse_config(config_text)
        self.assertEqual(config['app_name'], 'MyApp')
        self.assertEqual(config['version'], '1.0.3')

    def test_boolean_values(self):
        config_text = """
        debug_mode := true;
        maintenance := false;
        """
        config = parse_config(config_text)
        self.assertTrue(config['debug_mode'])
        self.assertFalse(config['maintenance'])

    def test_numeric_values(self):
        config_text = """
        max_connections := 15;
        timeout := {10 5 +};
        """
        config = parse_config(config_text)
        self.assertEqual(config['max_connections'], 15)
        self.assertEqual(config['timeout'], 15)

    def test_empty_values(self):
        config_text = """
        app_name := '';
        """
        config = parse_config(config_text)
        self.assertEqual(config['app_name'], '')

    def test_multi_block_parsing(self):
        config_text = """
        begin
            app_name := 'MyApp';
            version := '1.0.3';
            debug_mode := true;
            max_connections := {10 5 +};
        end

        begin
            database := 'app_db';
            user := 'admin';
            password := 'secret';
        end
        """
        config = parse_config(config_text)
        self.assertEqual(config['app_name'], 'MyApp')
        self.assertEqual(config['version'], '1.0.3')
        self.assertTrue(config['debug_mode'])
        self.assertEqual(config['max_connections'], 15)
        self.assertEqual(config['database'], 'app_db')
        self.assertEqual(config['user'], 'admin')
        self.assertEqual(config['password'], 'secret')

    def test_functions_max_sqrt(self):
        config_text = """
        max_value := {5 10 3 max()};
        sqrt_value := {25 sqrt()};
        """
        config = parse_config(config_text)
        self.assertEqual(config['max_value'], 10)
        self.assertEqual(config['sqrt_value'], 5.0)

    def test_constant_definition_and_usage(self):
        config_text = """
        (def a 96);
        (def b 2);
        result := {a b +};
        """
        config = parse_config(config_text)
        self.assertEqual(config['result'], 98)

    def test_function_mod(self):
        config_text = """
        result := {10 3 mod()};
        """
        config = parse_config(config_text)
        self.assertEqual(config['result'], 1)


if __name__ == "__main__":
    unittest.main()
