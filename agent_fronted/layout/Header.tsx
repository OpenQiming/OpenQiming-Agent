import React from 'react'
import { Layout } from 'antd'
import Image from 'next/image'
import back from './assets/back.png'
import user from './assets/user.png'
import { useAppContext } from '@/context/app-context'
import BackBtn from '@/app/components/base/back-btn'
const { Header } = Layout

type Props = {
  clickToAllPage?: (newActiveTab: string) => void
}

const TopHeader: React.FC<Props> = () => {
  const { userProfile } = useAppContext()
  return (
    <Header className='flex justify-between'
      style={{
        backgroundColor: '#FCFDFF',
        height: '60px',
        borderBottom: '1px solid #DEE5ED',
        boxShadow: '0px 1px 0px 0px #DEE5ED',
      }}>
      <div className="text-[20px] text-[#27292B] my-auto font-medium">启明网络大模型工具链</div>
      <div className='flex items-center'>
        <div onClick={() => {
          window.location.href = '/agent-platform-web-test/apps?category=all'
        }} style={{ cursor: 'pointer' }} >
          <Image src={back} alt='img' width={16} height={16} className='inline mt-[-5px]' />
          <span className='text-[14px] ml-[5px] text-[#6B7492]'><BackBtn title='返回首页' val='?category=all'></BackBtn></span>
        </div>
        {/* <span className='mx-[10px] text-[#DEE5ED] inline-block ml-[6px] mr-[6px]'>|</span> */}
        <div style={{ width: '1px', height: '20px', border: '1px solid #BDCEED', margin: '0 16px' }}></div>
        <div>
          <Image src={user} alt='img' width={32} height={32} className='inline mt-[-5px]' />
          <span className='text-[16px] ml-[5px] text-[#27292B]'>{userProfile?.name}</span>
        </div>
      </div>
    </Header>
  )
}

export default TopHeader
