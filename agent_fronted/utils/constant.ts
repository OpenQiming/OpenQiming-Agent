export const statusShow = (val: string) => {
  switch (val) {
    case 'draft':
      return {
        bgColor: 'bg-[#1B66FF]',
        statusName: '未发布',
        type: 'purple',
      }
    case 'published':
      return {
        bgColor: 'bg-[#EAF8DC]',
        statusName: '已发布',
        type: 'green',
      }
    case 'installed':
      return {
        bgColor: 'bg-[#0958d9]',
        statusName: '上架',
        type: 'blue',
      }
    case 'disabled':
      return {
        bgColor: 'bg-[#ff4d4f]',
        statusName: '禁用',
        type: 'error',
      }
    case '':
      return {
        bgColor: 'bg-[#faad14]',
        statusName: '无状态',
        type: 'warning',
      }
  }
}
export const statusRole = (val: string) => {
  switch (val) {
    case 'owner':
      return {
        bgColor: 'bg-[#0958d9]',
        role: '管理员',
        type: 'blue',
        size:600
      }
    case 'normal':
      return {
        bgColor: 'bg-[#0958d9]',
        role: '普通成员',
        type: 'blue',
        size:600
      }
  
  }
}