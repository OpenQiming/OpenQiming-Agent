export const getQueryParams = (key?: string) => {
  if (typeof window !== 'undefined') {
    const queryString = window.location.search
    const params = {} as any

    // 移除开头的问号
    const cleanedString = queryString.slice(1)

    // 拆分每个参数
    const pairs = cleanedString.split('&')

    pairs.forEach((pair) => {
      const [key, value] = pair.split('=')
      params[decodeURIComponent(key)] = decodeURIComponent(value || '')
    })

    return key ? params[key] : params
  }
}


export const getTenantIdFromUrl = () => {
  return getQueryParams('tenant_id')
}