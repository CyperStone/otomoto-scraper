from googletrans import Translator
from utils import load_json, save_json
from config import translation as translation_cfg


def get_translations(prompts):
    translator = Translator()
    return [t.text for t in translator.translate(prompts, src='pl', dest='en')]


def translate_column_values(column, translation_dict_path):
    translation_dict = load_json(translation_dict_path)

    unique_values = column.dropna().unique().tolist()
    values_without_translations = [value for value in unique_values if value not in translation_dict.keys()]

    if len(values_without_translations) > 0:
        missing_translations = get_translations(values_without_translations)
        for value_pl, value_eng in zip(values_without_translations, missing_translations):
            translation_dict[value_pl] = value_eng

        save_json(translation_dict, translation_dict_path)

    return column.replace(translation_dict)


def translate_offers_df(df, website_config):
    DICT_PATHS = translation_cfg.DICT_PATHS
    FEATURE_NAMES_DICT = website_config.FEATURE_NAMES_DICT

    try:
        df_eng = df.copy(deep=True)
        df_eng[FEATURE_NAMES_DICT['COLOR_NAME']] = translate_column_values(
            df_eng[FEATURE_NAMES_DICT['COLOR_NAME']], DICT_PATHS['COLOR_NAMES'])
        df_eng[FEATURE_NAMES_DICT['COLOR_TYPE']] = translate_column_values(
            df_eng[FEATURE_NAMES_DICT['COLOR_TYPE']], DICT_PATHS['COLOR_TYPES'])
        df_eng[FEATURE_NAMES_DICT['BODY_TYPE']] = translate_column_values(
            df_eng[FEATURE_NAMES_DICT['BODY_TYPE']], DICT_PATHS['BODY_TYPES'])
        df_eng[FEATURE_NAMES_DICT['SELLER_TYPE']] = translate_column_values(
            df_eng[FEATURE_NAMES_DICT['SELLER_TYPE']], DICT_PATHS['SELLER_TYPES'])
        df_eng[FEATURE_NAMES_DICT['FUEL_TYPE']] = translate_column_values(
            df_eng[FEATURE_NAMES_DICT['FUEL_TYPE']], DICT_PATHS['FUEL_TYPES'])
        df_eng[FEATURE_NAMES_DICT['TRANSMISSION_TYPE']] = translate_column_values(
            df_eng[FEATURE_NAMES_DICT['TRANSMISSION_TYPE']], DICT_PATHS['TRANSMISSION_TYPES'])
        df_eng[FEATURE_NAMES_DICT['DRIVE_TYPE']] = translate_column_values(
            df_eng[FEATURE_NAMES_DICT['DRIVE_TYPE']], DICT_PATHS['DRIVE_TYPES'])
        df_eng[FEATURE_NAMES_DICT['CONDITION']] = translate_column_values(
            df_eng[FEATURE_NAMES_DICT['CONDITION']], DICT_PATHS['CONDITION_TYPES'])
        df_eng[FEATURE_NAMES_DICT['ORIGIN_COUNTRY']] = translate_column_values(
            df_eng[FEATURE_NAMES_DICT['ORIGIN_COUNTRY']], DICT_PATHS['COUNTRY_NAMES'])

        columns_translation_dict = load_json(DICT_PATHS['COLUMN_NAMES'])
        column_names_without_translations = [col for col in df_eng.columns
                                             if col not in columns_translation_dict.keys()]

        if len(column_names_without_translations) > 0:
            missing_translations = get_translations(column_names_without_translations)
            for col_pl, col_eng in zip(column_names_without_translations, missing_translations):
                columns_translation_dict[col_pl] = col_eng

            save_json(columns_translation_dict, DICT_PATHS['COLUMN_NAMES'])

        df_eng.columns = [columns_translation_dict[col] for col in df_eng.columns]

    except Exception as e:
        print(f'Offers DataFrame translation failed due to: {e}')
        return False, df

    return True, df_eng
