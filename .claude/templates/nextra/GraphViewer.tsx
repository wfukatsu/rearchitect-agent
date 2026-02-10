import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'

interface Node {
  id: string
  name: string
  type: string
  group?: string
}

interface Link {
  source: string
  target: string
  type: string
}

interface GraphData {
  nodes: Node[]
  links: Link[]
}

export default function GraphViewer({ dataPath }: { dataPath: string }) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [stats, setStats] = useState({ nodes: 0, edges: 0 })

  useEffect(() => {
    if (!svgRef.current) return

    // Load graph data
    fetch(dataPath)
      .then(res => res.json())
      .then((data: GraphData) => {
        setStats({
          nodes: data.nodes.length,
          edges: data.links.length
        })

        renderGraph(data)
      })
      .catch(err => {
        console.error('Failed to load graph data:', err)
      })
  }, [dataPath])

  const renderGraph = (data: GraphData) => {
    if (!svgRef.current) return

    const svg = d3.select(svgRef.current)
    const width = svgRef.current.clientWidth
    const height = 600

    svg.selectAll('*').remove()
    svg.attr('width', width).attr('height', height)

    // Color mapping
    const colorMap: Record<string, string> = {
      Domain: '#e74c3c',
      Entity: '#3498db',
      Term: '#2ecc71',
      ValueObject: '#f39c12',
      Aggregate: '#9b59b6',
      Service: '#1abc9c'
    }

    // Create force simulation
    const simulation = d3
      .forceSimulation(data.nodes as any)
      .force(
        'link',
        d3
          .forceLink(data.links)
          .id((d: any) => d.id)
          .distance(100)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30))

    // Add zoom behavior
    const g = svg.append('g')
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom as any)

    // Draw links
    const link = g
      .append('g')
      .selectAll('line')
      .data(data.links)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2)

    // Draw nodes
    const node = g
      .append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter()
      .append('circle')
      .attr('r', 10)
      .attr('fill', (d) => colorMap[d.type] || '#95a5a6')
      .call(
        d3
          .drag<SVGCircleElement, Node>()
          .on('start', (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on('drag', (event, d: any) => {
            d.fx = event.x
            d.fy = event.y
          })
          .on('end', (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
          }) as any
      )

    // Add labels
    const label = g
      .append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter()
      .append('text')
      .text((d) => d.name)
      .attr('font-size', 12)
      .attr('fill', '#333')
      .attr('dx', 15)
      .attr('dy', 4)

    // Tooltip
    const tooltip = d3
      .select('body')
      .append('div')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background', 'rgba(0, 0, 0, 0.8)')
      .style('color', '#fff')
      .style('padding', '8px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('z-index', '1000')

    node
      .on('mouseover', (event, d) => {
        tooltip
          .style('visibility', 'visible')
          .html(`<strong>${d.name}</strong><br/>Type: ${d.type}${d.group ? `<br/>Group: ${d.group}` : ''}`)
      })
      .on('mousemove', (event) => {
        tooltip
          .style('top', event.pageY - 10 + 'px')
          .style('left', event.pageX + 10 + 'px')
      })
      .on('mouseout', () => {
        tooltip.style('visibility', 'hidden')
      })

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y)

      label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y)
    })

    // Search functionality
    const handleSearch = (term: string) => {
      if (!term) {
        node.attr('opacity', 1)
        label.attr('opacity', 1)
        link.attr('opacity', 0.6)
        return
      }

      const lowerTerm = term.toLowerCase()
      node.attr('opacity', (d) =>
        d.name.toLowerCase().includes(lowerTerm) ? 1 : 0.2
      )
      label.attr('opacity', (d) =>
        d.name.toLowerCase().includes(lowerTerm) ? 1 : 0.2
      )
      link.attr('opacity', 0.2)
    }

    // Expose search function
    ;(window as any).graphSearch = handleSearch
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value
    setSearchTerm(term)
    if ((window as any).graphSearch) {
      ;(window as any).graphSearch(term)
    }
  }

  return (
    <div className="graph-viewer">
      <div
        style={{
          position: 'absolute',
          padding: '10px',
          background: 'rgba(255,255,255,0.9)',
          borderRadius: '5px',
          margin: '10px',
          zIndex: 100
        }}
      >
        <input
          type="text"
          placeholder="Search nodes..."
          value={searchTerm}
          onChange={handleSearchChange}
          style={{
            width: '180px',
            padding: '5px',
            border: '1px solid #ccc',
            borderRadius: '4px'
          }}
        />
        <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
          Nodes: {stats.nodes} | Edges: {stats.edges}
        </div>
      </div>
      <svg ref={svgRef} style={{ width: '100%', height: '600px' }}></svg>
      <div style={{ marginTop: '15px', display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: '12px',
              height: '12px',
              background: '#e74c3c',
              borderRadius: '50%',
              marginRight: '5px'
            }}
          ></span>
          Domain
        </span>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: '12px',
              height: '12px',
              background: '#3498db',
              borderRadius: '50%',
              marginRight: '5px'
            }}
          ></span>
          Entity
        </span>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: '12px',
              height: '12px',
              background: '#2ecc71',
              borderRadius: '50%',
              marginRight: '5px'
            }}
          ></span>
          Term
        </span>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: '12px',
              height: '12px',
              background: '#f39c12',
              borderRadius: '50%',
              marginRight: '5px'
            }}
          ></span>
          ValueObject
        </span>
        <span>
          <span
            style={{
              display: 'inline-block',
              width: '12px',
              height: '12px',
              background: '#9b59b6',
              borderRadius: '50%',
              marginRight: '5px'
            }}
          ></span>
          Aggregate
        </span>
      </div>
    </div>
  )
}
