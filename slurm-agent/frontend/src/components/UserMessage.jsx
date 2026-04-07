// components/UserMessage.jsx
import { memo } from 'react'

const UserMessage = memo(function UserMessage({ content }) {
  return (
    <div className="row row-user">
      <div className="bubble bubble-user">{content}</div>
    </div>
  )
})

export default UserMessage
