export const buildFields = (fields, options) => {
  return fields.map((f) => ({
    ...f,
    options: options.data?.[f.name] || [],
    // options: optionsData?.[f.optionKey] || [],
  }));
};
