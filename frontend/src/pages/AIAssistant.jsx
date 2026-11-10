import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router'

function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Hello! I'm NetGuard AI Assistant. " +
        "Ask me about DDoS attacks, network security, " +
        "or how NetGuard AI works."
    }
  ])

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const location = useLocation()
  const navigate = useNavigate()

  const predictionId = location.state?.predictionId

  const bottomRef = useRef(null)
  const sendingRef = useRef(false)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: 'smooth'
    })
  }, [messages, loading])

  const sendMessage = async (event) => {
    event.preventDefault()

    const question = input.trim()

    if (!question || sendingRef.current) return

    sendingRef.current = true

    // Uzimamo najvise 10 prethodnih poruka.
    // Pocetnu pozdravnu poruku ne saljemo API-ju.
    const history = messages.slice(1).slice(-10)

    setMessages((prev) => [
      ...prev,
      { role: 'user', content: question }
    ])

    setInput('')
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/v1/chat',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: question,
            history
          })
        }
      )

      if (!response.ok) {
        let detail = 'Unable to get AI response.'

        try {
          const errorData = await response.json()
          if (typeof errorData.detail === 'string') {
            detail = errorData.detail
          }
        } catch {
          // Zadrzavamo podrazumijevanu poruku.
        }

        throw new Error(detail)
      }

      
const data = await response.json()

// Provjeravamo da li je backend vratio ispravan odgovor
if (
  !data ||
  typeof data.reply !== 'string' ||
  !data.reply.trim()
) {
  throw new Error(
    'Backend nije vratio ispravan AI odgovor.'
  )
}

setMessages((prev) => [
  ...prev,
  {
    role: 'assistant',
    content: data.reply
  }
])


    } catch (err) {
      console.error(err)
      setError(err.message || 'Something went wrong.')

    } finally {
      sendingRef.current = false
      setLoading(false)
    }
  }
useEffect(() => {
  if (!predictionId) return

  setInput(`Explain prediction ${predictionId}`)

  navigate(location.pathname, {
    replace: true,
    state: null
  })
}, [predictionId, navigate, location.pathname])
  const clearChat = () => {
    if (sendingRef.current) return

    setMessages([
      {
        role: 'assistant',
        content:
          "Hello! I'm NetGuard AI Assistant. " +
          "How can I help you today?"
      }
    ])

    setError(null)
    setInput('')
  }

  return (
    <div className="chat-page">

      <div className="chat-page-header">
        <div>
          <h1>AI Security Assistant</h1>
          <p>
            Ask questions about cybersecurity,
            DDoS detection and network protection.
          </p>
        </div>

        <button
          type="button"
          className="chat-clear-button"
          onClick={clearChat}
          disabled={loading}
        >
          Clear Chat
        </button>
      </div>

      <div className="chat-container">

        <div className="chat-container-header">
          <div className="chat-avatar">AI</div>

          <div>
            <h3>NetGuard AI Assistant</h3>
            <span>Cybersecurity Support</span>
          </div>
        </div>

        <div className="chat-messages">

          {messages.map((message, index) => (
            <div
              key={index}
              className={
                `chat-message ${message.role}`
              }
            >
              {message.role === 'assistant' && (
                <div className="chat-message-avatar">
                  AI
                </div>
              )}

              <div className="chat-bubble">
                {message.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="chat-message assistant">
              <div className="chat-message-avatar">
                AI
              </div>

              <div className="chat-bubble chat-typing">
                AI is thinking...
              </div>
            </div>
          )}

          <div ref={bottomRef} />

        </div>

        {error && (
          <p className="chat-error">{error}</p>
        )}

        <form
          className="chat-input-area"
          onSubmit={sendMessage}
        >
          <input
            type="text"
            placeholder="Ask a cybersecurity question..."
            value={input}
            maxLength={2000}
            onChange={(event) =>
              setInput(event.target.value)
            }
            disabled={loading}
          />

          <button
            type="submit"
            disabled={loading || !input.trim()}
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>

      </div>

    </div>
  )
}

export default AIAssistant
